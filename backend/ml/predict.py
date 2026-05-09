import os
import torch
import logging
import numpy as np
from pathlib import Path
from torchvision import transforms
from torchvision.models import resnet50
from PIL import Image

logger = logging.getLogger(__name__)

DEVICE = "cpu"
logger.info(f"Using device: {DEVICE}")

MODEL_PATH = Path(__file__).parent / "model.pth"
logger.info(f"Model path: {MODEL_PATH}")

CLASS_NAMES = ["macrovesicular", "normal", "microvesicular"]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# =========================
# load model
# =========================
logger.info("Loading model...")
model = resnet50(num_classes=3)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.to(DEVICE)
model.eval()
logger.info("Model loaded successfully")

# =========================
# prediction
# =========================
def predict_tiles(tile_dir: str):
    import traceback
    from collections import Counter

    logger.info(f"predict_tiles called with tile_dir={tile_dir}")
    predictions = []
    confidences = []
    files = os.listdir(tile_dir)
    logger.info(f"Found {len(files)} files in tile_dir")
    
    for idx, filename in enumerate(files):
        logger.info(f"Processing file {idx+1}/{len(files)}: {filename}")
        path = os.path.join(tile_dir, filename)
        
        try:
            logger.info(f"Opening image: {path}")
            img = Image.open(path).convert('RGB')
            logger.info(f"Image opened, original size: {img.size}")
            
            logger.info("Resizing image...")
            img = img.resize((224, 224), Image.LANCZOS)
            logger.info(f"Resized to: {img.size}")
            
            logger.info("Converting to numpy array...")
            np_img = np.array(img, dtype=np.float32) / 255.0
            logger.info(f"numpy array shape: {np_img.shape}")
            
            logger.info("Transposing to CHW...")
            np_img = np_img.transpose((2, 0, 1))
            logger.info(f"After transpose shape: {np_img.shape}")
            
            logger.info("Creating tensor and moving to device...")
            tensor = torch.from_numpy(np_img).unsqueeze(0).to(DEVICE)
            logger.info(f"Tensor shape: {tensor.shape}, device: {tensor.device}")
            
            logger.info("Running inference...")
            logger.info("Setting number of threads to 1")
            torch.set_num_threads(1)
            logger.info("Model forward pass start")
            with torch.no_grad():
                outputs = model(tensor)
                logger.info("Model forward pass done")
                probs = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probs, dim=1)
            logger.info(f"Inference done: class {predicted.item()}, confidence {confidence.item()}")
            
            predictions.append(predicted.item())
            confidences.append(confidence.item())
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            logger.error(traceback.format_exc())
            continue
    
    if not predictions:
        raise ValueError("No predictions were made, check tile directory contents.")
    
    counter = Counter(predictions)
    final_class = counter.most_common(1)[0][0]
    avg_confidence = sum(confidences) / len(confidences)
    logger.info(f"Final prediction: {CLASS_NAMES[final_class]}, avg confidence: {avg_confidence}")
    
    return {
        "prediction": CLASS_NAMES[final_class],
        "confidence": avg_confidence
    }