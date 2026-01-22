import tensorflow as tf
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelOptimizer")

def convert_to_tflite(h5_path, tflite_path):
    """Convert Keras .h5 model to TensorFlow Lite .tflite model"""
    try:
        if not os.path.exists(h5_path):
            logger.error(f"Input model not found: {h5_path}")
            return False

        logger.info(f"Loading model from {h5_path}...")
        model = tf.keras.models.load_model(h5_path)
        
        logger.info("Converting to TFLite...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Enable optimizations
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        tflite_model = converter.convert()
        
        logger.info(f"Saving TFLite model to {tflite_path}...")
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
            
        logger.info("Conversion successful!")
        
        # Compare sizes
        h5_size = os.path.getsize(h5_path) / (1024*1024)
        tflite_size = os.path.getsize(tflite_path) / (1024*1024)
        logger.info(f"Original Size: {h5_size:.2f} MB")
        logger.info(f"Optimized Size: {tflite_size:.2f} MB")
        logger.info(f"Reduction: {(1 - tflite_size/h5_size)*100:.1f}%")
        
        return True
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return False

if __name__ == "__main__":
    h5_path = "models/emotion_detection.h5"
    tflite_path = "models/emotion_detection.tflite"
    
    # Create models dir if not exists (though it should)
    os.makedirs("models", exist_ok=True)
    
    # If h5 doesn't exist but we are in dev environment, maybe we need to create a dummy one or fail
    if not os.path.exists(h5_path):
        print(f"Error: {h5_path} not found. Please place your model file there first.")
    else:
        convert_to_tflite(h5_path, tflite_path)
