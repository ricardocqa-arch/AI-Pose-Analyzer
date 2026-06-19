import cv2
import mediapipe as mp
import numpy as np
import json
import os

from paths import resource_path
from datetime import timedelta, datetime
from tqdm import tqdm
from config import RISK_CONFIG
import unicodedata

from recommendation import recomendar_exoesqueletos
from PIL import Image, ImageDraw, ImageFont


def remove_acentos(texto):
    """Remove acentos para cv2.putText"""
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


# ===================== MEDIA PIPE SETUP =====================
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.75,
    model_complexity=2,
    smooth_landmarks=True

)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def calculate_angle(a, b, c):
    """Calcula ângulo entre 3 pontos"""
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return angle


def get_posture_angles(lm, w, h):
    """Calcula todos os ângulos importantes de forma consistente"""
    def p(idx):
        lm_pt = lm.landmark[idx]
        return np.array([lm_pt.x * w, lm_pt.y * h])

    nose = p(0)
    l_shoulder = p(11)
    r_shoulder = p(12)
    l_hip = p(23)
    r_hip = p(24)
    l_knee = p(25)
    r_knee = p(26)
    l_ankle = p(27)
    r_ankle = p(28)
    l_elbow = p(13)
    r_elbow = p(14)

    return {
        'trunk':      calculate_angle(l_shoulder, l_hip, l_knee),      # ~180° ereto
        'neck':       calculate_angle(nose, l_shoulder, l_hip),
        'shoulder_l': calculate_angle(l_elbow, l_shoulder, l_hip),
        'shoulder_r': calculate_angle(r_elbow, r_shoulder, r_hip),
        'arm_l':      calculate_angle(l_hip, l_shoulder, l_elbow),
        'arm_r':      calculate_angle(r_hip, r_shoulder, r_elbow),
        'knee_l':     calculate_angle(l_hip, l_knee, l_ankle),
        'knee_r':     calculate_angle(r_hip, r_knee, r_ankle),
    }


def adicionar_watermark(frame, logo_path = resource_path("logo.png"), opacity=0.3, position="top-right"):
    if not os.path.exists(logo_path):
        return frame

    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo is None:
        return frame

    scale = 0.25
    new_width = int(frame.shape[1] * scale)
    aspect = logo.shape[0] / logo.shape[1]
    new_height = int(new_width * aspect)
    logo = cv2.resize(logo, (new_width, new_height))

    h, w = frame.shape[:2]
    lh, lw = logo.shape[:2]

    if position == "bottom-right":
        x, y = w - lw - 20, h - lh - 20
    elif position == "top-right":
        x, y = w - lw - 20, 20
    else:
        x, y = 20, 20

    if logo.shape[2] == 4:
        overlay = logo[:, :, :3]
        alpha = logo[:, :, 3] / 255.0 * opacity
        for c in range(3):
            frame[y:y+lh, x:x+lw, c] = (1.0 - alpha) * frame[y:y+lh, x:x+lw, c] + alpha * overlay[:, :, c]
    else:
        frame[y:y+lh, x:x+lw] = cv2.addWeighted(frame[y:y+lh, x:x+lw], 1 - opacity, logo, opacity, 0)

    return frame


def resize_with_aspect_ratio(frame, target_width, target_height):
    h, w = frame.shape[:2]
    aspect = w / h
    target_aspect = target_width / target_height

    if aspect > target_aspect:
        new_h = int(target_width / aspect)
        resized = cv2.resize(frame, (target_width, new_h))
        delta = (target_height - new_h) // 2
        final = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        final[delta:delta + new_h, :] = resized
    else:
        new_w = int(target_height * aspect)
        resized = cv2.resize(frame, (new_w, target_height))
        delta = (target_width - new_w) // 2
        final = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        final[:, delta:delta + new_w] = resized
    return final


def analisar_video(video_path, peso_carga=0, pasta_destino="."):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    base = os.path.splitext(os.path.basename(video_path))[0]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    annotated_video = os.path.join(pasta_destino, f"ANOTADO_{base}_{ts}.mp4")
    json_file = os.path.join(pasta_destino, f"resultados_{base}_{ts}.json")

    # Melhor codec para compatibilidade web
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    out = cv2.VideoWriter(annotated_video, fourcc, fps, (width, height))

    print(f"🎥 Processando vídeo: {os.path.basename(video_path)}")

    # ===================== VÍDEO DE ABERTURA =====================
    #abertura_path = resource_path("video abertura.mp4")
    #if os.path.exists(abertura_path):
        #cap_abertura = cv2.VideoCapture(abertura_path)
        #while True:
            #ret, frame = cap_abertura.read()
            #if not ret:
              #  break
            #frame = resize_with_aspect_ratio(frame, width, height)
            #out.write(frame)
        #cap_abertura.release()

    # ===================== PROCESSAMENTO PRINCIPAL =====================
    events = []
    active_risks = {k: None for k in RISK_CONFIG}
    frame_count = 0

    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for _ in tqdm(range(total_frames), desc="Analisando postura"):
            ret, frame = cap.read()
            if not ret:
                break

            timestamp_sec = frame_count / fps
            timestamp_str = str(timedelta(seconds=timestamp_sec))[:10]

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)

            angles = None
            if results.pose_landmarks:
                lm = results.pose_landmarks
                angles = get_posture_angles(lm, width, height)

                # Desenhar skeleton
                mp_drawing.draw_landmarks(
                    frame, lm, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )

            # ===================== DETEÇÃO DE RISCOS =====================
            alerta_ativo = []

            if angles:
                for risco_key, config in RISK_CONFIG.items():
                    alerta = False
                    max_ang = config["max_angulo"]

                    if risco_key == "flexao_tronco":
                        flexion = 180 - angles['trunk']
                        alerta = flexion > max_ang
                    elif risco_key == "flexao_pescoco":
                        alerta = angles['neck'] < max_ang
                    elif risco_key == "elevacao_ombro":
                        alerta = angles['shoulder_l'] > max_ang or angles['shoulder_r'] > max_ang
                    elif risco_key == "flexao_joelho":
                        alerta = angles['knee_l'] < max_ang or angles['knee_r'] < max_ang
                    elif risco_key == "elevacao_braco":
                        alerta = angles['arm_l'] > max_ang or angles['arm_r'] > max_ang

                    if alerta:
                        if active_risks[risco_key] is None:
                            active_risks[risco_key] = timestamp_sec
                        if (timestamp_sec - active_risks[risco_key]) >= 0.8:
                            alerta_ativo.append(config['nome'])
                    else:
                        if active_risks[risco_key] is not None:
                            duracao = timestamp_sec - active_risks[risco_key]
                            if duracao >= config.get("min_duracao_seg", 1.5):
                                events.append({
                                    "tipo": config["nome"],
                                    "inicio": str(timedelta(seconds=active_risks[risco_key]))[:10],
                                    "fim": timestamp_str,
                                    "duracao_seg": round(duracao, 2),
                                    "carga_kg": float(peso_carga) if peso_carga > 0 else "Não aplicável"
                                })
                            active_risks[risco_key] = None


            if alerta_ativo:
                y_pos = 50
                for nome_risco in alerta_ativo:
                    texto = f"ALERTA: {remove_acentos(nome_risco)}"
                    cv2.putText(frame, texto, (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX,
                                0.85, (0, 165, 255), 2, cv2.LINE_AA)
                    y_pos += 40

            frame = adicionar_watermark(frame, opacity=0.55)
            out.write(frame)
            frame_count += 1

    finally:
        cap.release()

    # ===================== SLIDE FINAL =====================
    print("📋 Gerando slide final...")
    recomendacao_texto = recomendar_exoesqueletos(events)

    slide_img = Image.new("RGB", (width, height), color=(15, 20, 40))
    draw = ImageDraw.Draw(slide_img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 55)
        font_text = ImageFont.truetype("arial.ttf", 32)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    draw.text((80, 70), "RECOMENDAÇÕES DE EXOESQUELETOS", font=font_title, fill=(0, 200, 255))

    y = 160
    for line in recomendacao_texto.split('\n'):
        if line.strip():
            draw.text((80, y), line.strip(), font=font_text, fill=(240, 240, 255))
            y += 55

    final_slide = cv2.cvtColor(np.array(slide_img), cv2.COLOR_RGB2BGR)

    # slide final
    last_frame = frame if 'frame' in locals() else np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(int(fps * 1.5)):
        alpha = 1 - (i / (fps * 1.5))
        fade = cv2.addWeighted(last_frame, alpha, final_slide, 1 - alpha, 0)
        out.write(fade)

    for _ in range(int(fps * 8)):
        out.write(final_slide)

    # Vídeo de fecho
    #final_path = resource_path("video final.mp4")
    #if os.path.exists(final_path):
        #cap_final = cv2.VideoCapture(final_path)
        #while True:
            #ret, frame = cap_final.read()
            #if not ret:
               # break
            #frame = resize_with_aspect_ratio(frame, width, height)
            #out.write(frame)
        #cap_final.release()

    out.release()

    # ===================== SALVAR JSON =====================
    resultado = {
        "video": os.path.basename(video_path),
        "eventos": sorted(events, key=lambda x: x["inicio"])
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"✅ Vídeo processado com sucesso: {annotated_video}")
    return events, annotated_video, json_file