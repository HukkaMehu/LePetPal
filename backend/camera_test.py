
import cv2
import sys

def test_camera(index: int):
    """Tests a camera at a given index."""
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"--- Camera index {index}: FAILED to open. ---")
        return

    print(f"--- Camera index {index}: Successfully opened. ---")
    ret, frame = cap.read()
    if ret and frame is not None:
        print(f"--- Camera index {index}: Successfully read a frame (resolution: {frame.shape[1]}x{frame.shape[0]}). ---")
    else:
        print(f"--- Camera index {index}: FAILED to read a frame. ---")
    cap.release()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test a specific index provided as an argument
        try:
            index_to_test = int(sys.argv[1])
            test_camera(index_to_test)
        except ValueError:
            print("Please provide a valid number for the camera index.")
    else:
        # Test the first 5 indices
        print("Testing camera indices 0 through 4...")
        for i in range(5):
            test_camera(i)
