# 🐾 LePetPal - AI-Powered Pet Robot

An intelligent robotic pet companion powered by LeRobot ACT (Action Chunking Transformer) models and real-time vision AI. LePetPal can play fetch, interact with pets, and learn new behaviors through imitation learning.

## 🎯 Project Overview

LePetPal is a hackathon project that combines:
- **LeRobot Framework**: ACT policy for robotic control
- **SO-100 Follower Arm**: 6DOF robotic arm hardware
- **Real-time Vision**: Camera-based object detection and tracking
- **Dataset Replay**: Pre-recorded demonstrations from HuggingFace
- **Live Inference**: ACT model running on live camera feed

---

## 🏗️ System Architecture

LePetPal uses a **distributed two-service architecture** that separates hardware control from user interface:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER BROWSER                                      │
│                  (anywhere in the world)                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓ HTTPS
┌─────────────────────────────────────────────────────────────────────┐
│              WEB FRONTEND SERVICE (Vercel/Cloud)                     │
│                   Next.js + React + TypeScript                       │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Live Video   │  │   Command    │  │  Analytics   │             │
│  │   Player     │  │   Buttons    │  │  Dashboard   │             │
│  │  (MJPEG)     │  │ (REST API)   │  │   (Charts)   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓ HTTPS via Cloudflare Tunnel
                   (https://robot-abc123.trycloudflare.com)
                             │
                             ↓ Forwards to localhost:5000
┌─────────────────────────────────────────────────────────────────────┐
│         ROBOT BACKEND SERVICE (Local Device with Hardware)           │
│                    Flask + Python + LeRobot                          │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Camera     │  │  ACT Model   │  │  Dataset     │             │
│  │  Capture     │  │  Inference   │  │   Replay     │             │
│  │  + MJPEG     │  │ (LeRobot)    │  │ (HuggingFace)│             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                      │
│         └──────────────────┼──────────────────┘                      │
│                            ↓                                         │
│                   ┌────────────────┐                                │
│                   │  ArmAdapter    │                                │
│                   │  SafetyManager │                                │
│                   │  ServoAdapter  │                                │
│                   └────────┬───────┘                                │
└────────────────────────────┼────────────────────────────────────────┘
                             ↓ USB Connection
                   ┌─────────────────────┐
                   │   SO-100 Robot Arm  │
                   │   + USB Camera      │
                   │   + Treat Dispenser │
                   └─────────────────────┘
```

### Service 1: Robot Backend (Flask on Local Device)
**Location**: Runs on computer **physically connected to robot hardware**  
**Technology**: Python Flask  
**Port**: `localhost:5000` (exposed via tunnel)

**Responsibilities**:
- Direct USB control of SO-100 robotic arm via LeRobot
- Camera capture and MJPEG streaming with AI overlays
- ACT model inference for real-time robot control
- Dataset replay from HuggingFace (Shrek0/pet_main, Shrek0/throw_main)
- Servo control for treat dispenser
- Text-to-speech for pet interaction
- Safety constraints and calibration

**REST API Endpoints**:
```
GET  /health              → Health check
GET  /video_feed          → MJPEG camera stream with overlays
POST /command             → Execute robot behavior (0=pet, 1=throw, 2=ACT)
GET  /status/{id}         → Poll command execution status
POST /dispense_treat      → Trigger treat dispenser servo
POST /speak               → Text-to-speech output
```

### Service 2: Web Frontend (Next.js on Cloud)
**Location**: Deployed separately (Vercel/Netlify/Cloud)  
**Technology**: Next.js 14 + React + TypeScript + Tailwind

**Responsibilities**:
- User interface for remote pet monitoring
- Live video player consuming `/video_feed`
- Command buttons (Play with Ball, Give Treat, Go Home, Speak)
- Status polling and UI feedback
- Analytics dashboard and event history
- Routine builder for scheduled behaviors

**Communication**:
```typescript
// Frontend configuration
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL
  // e.g., "https://robot-abc123.trycloudflare.com"

// API calls to robot backend
fetch(`${BACKEND_URL}/command`, {
  method: 'POST',
  body: JSON.stringify({ command: 2 })
})

// Video stream
<img src={`${BACKEND_URL}/video_feed`} />
```

### The Bridge: Cloudflare Tunnel
**Problem**: Robot backend runs on `localhost:5000` but needs to be accessible from cloud-hosted frontend.

**Solution**: Secure HTTPS tunnel exposes local backend to internet:
```bash
# Start Cloudflare Tunnel
cloudflared tunnel --url http://localhost:5000
# Returns: https://robot-abc123.trycloudflare.com
```

This URL is configured in the frontend's environment variables, enabling the remote web app to communicate with the local robot service.

### Why This Architecture?

1. **Hardware Isolation**: Robot control stays local with direct USB access
2. **Global Access**: Frontend on CDN provides fast access from anywhere
3. **Security**: HTTPS tunnel without exposing raw IP address
4. **Scalability**: Frontend scales independently; backend handles one job at a time
5. **Development**: Teams can work on frontend and backend separately with clear API contract

---

## 📋 Repository Structure

### Backend Implementations (Multiple Branches)

Due to parallel development and different feature sets, there are **multiple backend branches**:

#### 🔵 **backend-branch** (Recommended for Dataset Replay)
- **Purpose**: Dataset replay from HuggingFace + NEW ACT model support
- **Features**:
  - ✅ `command=0`: Replay pet_main dataset (petting motions)
  - ✅ `command=1`: Replay throw_main dataset (throwing motions)
  - ✅ `command=2`: ACT model live inference (NEW!)
  - ✅ Backwards compatible with original implementation
  - ✅ Inline LeRobotDataset replay in Flask endpoint
- **Status**: ✅ Production ready, backwards compatible
- **Use Case**: When you want pre-recorded demonstrations + optional ACT model

#### 🟢 **backend** (Main Development)
- **Purpose**: Full-featured development branch with ACT model integration
- **Features**:
  - ✅ CommandManager with policy-based execution
  - ✅ Auto-cancel for conflicting commands
  - ✅ Separate policy methods (pick_up_the_ball, throw_ball, go_home)
  - ✅ ACT model inference with LeRobot
  - ✅ Safety manager with calibration support
  - ✅ Mock hardware for testing without robot
- **Status**: ✅ Active development
- **Use Case**: When you want full control and extensibility

#### 🟡 **backend-with-replay** 
- **Purpose**: Experimental merge of dataset replay with ACT model
- **Features**:
  - ✅ Contains lerobot_worker.py, robot_runner.py
  - ✅ Dataset replay functionality
  - ✅ Test scripts for robot operations
- **Status**: 🔄 Experimental
- **Use Case**: Reference implementation for combined features

#### 🔴 **act-model-integration** (Archived)
- **Purpose**: Initial ACT model integration experiments
- **Status**: 📦 Archived/Reference only
- **Note**: Merged into main development branches

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.10+ required
python --version

# Install dependencies
pip install -r backend/requirements.txt

# For development
pip install -r backend/requirements-dev.txt
```

### Configuration
Create a `.env` file in the project root:

```env
# Server
PORT=5000
USE_HARDWARE=false  # Set to true when connected to real robot

# Camera
CAMERA_INDEX=0
STREAM_RES=1280x720

# Model Configuration
MODEL_MODE=lerobot_policy  # Options: 'scripted' | 'lerobot_policy'
MODEL_PATH=C:\path\to\pretrained_model
DEVICE=cpu  # Options: 'cpu' | 'cuda' | 'privateuseone:0' (DirectML)
INFERENCE_RATE_HZ=15

# Robot Hardware (when USE_HARDWARE=true)
ROBOT_PORT=/dev/tty.usbmodem5A460836061
ROBOT_ID=full_new
LEROBOT_PORT=/dev/tty.usbmodem5A460836061
LEROBOT_ID=full_new

# Safety
CALIBRATION_PATH=backend/config/calibration.json
```

### Running the Backend

#### Option 1: Dataset Replay (backend-branch)
```bash
git checkout backend-branch
cd backend
python app.py
```

API Usage:
```bash
# Pet the pet (dataset replay)
curl -X POST http://localhost:5000/command -H "Content-Type: application/json" -d '{"command": 0}'

# Throw ball (dataset replay)
curl -X POST http://localhost:5000/command -H "Content-Type: application/json" -d '{"command": 1}'

# ACT model inference (NEW!)
curl -X POST http://localhost:5000/command -H "Content-Type: application/json" -d '{"command": 2}'
```

#### Option 2: Full Development Backend (backend)
```bash
git checkout backend
cd backend
python run_backend.py
```

---

## 🏗️ Architecture

### Model Pipeline (ACT Model)
```
Camera Feed → Image Preprocessing → ACT Policy → Action Postprocessing → Robot Arm
     ↓              ↓                    ↓              ↓                    ↓
  1920x1080     RGB, CHW           select_action()   6D targets      SO-100 Follower
  BGR frame     [0,1] float32      (inference)       (degrees)       move_to_position()
```

### Expected Input/Output
- **Input**: 
  - Visual: `observation.images.front` (3, 1080, 1920) - RGB camera feed
  - State: `observation.state` (6,) - Joint positions [shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper]
  
- **Output**: 
  - Actions: (6,) - Target joint positions in degrees

### Backend Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/health` | GET | Server health check | `{"status": "ok", "api": 1}` |
| `/command` | POST | Execute robot command | `{"request_id": "uuid"}` (202) |
| `/status/:id` | GET | Check command status | `{"state": "executing", "phase": "...", "message": "..."}` |
| `/video_feed` | GET | MJPEG camera stream | Multipart MJPEG stream |
| `/speak` | POST | Text-to-speech | `{"status": "ok"}` |
| `/dispense` | POST | Dispense treat (servo) | `{"status": "ok"}` |

---

## 🗂️ Project Files

### Core Backend Files
```
backend/
├── app.py                    # Flask application (main entry point)
├── run_backend.py           # Alternative runner
├── command_manager.py       # Policy-based command execution
├── model_runner.py          # ACT model inference engine
├── autonomous_manager.py    # Autonomous behavior controller
├── safety.py                # Safety constraints and calibration
├── video.py                 # Camera capture and streaming
├── status_store.py          # Request status tracking
├── adapters/
│   ├── arm_adapter.py      # SO-100 arm control (real + mock)
│   ├── servo_adapter.py    # Treat dispenser servo
│   └── tts.py              # Text-to-speech adapter
├── config/
│   └── calibration.example.json  # Safety calibration template
├── tests/
│   └── test_contract_smoke.py    # API contract tests
└── tools/
    ├── check_*.py          # Diagnostic utilities
    ├── robot_sanity.py     # Hardware sanity checks
    └── test_*.py           # Integration tests
```

### Documentation
```
├── API_DOCUMENTATION.md           # REST API reference
├── ARCHITECTURE_DECISION.md       # Design decisions
├── FRONTEND_INTEGRATION.md        # Frontend integration guide
├── TESTING_GUIDE.md              # Testing procedures
├── VIDEO_OPTIMIZATION.md         # Camera streaming optimization
├── BACKWARDS_COMPATIBILITY_REPORT.md  # Compatibility analysis
└── backend_architecture.md       # Backend architecture deep-dive
```

### Datasets (HuggingFace)
- **Shrek0/pet_main**: Petting demonstrations
- **Shrek0/throw_main**: Ball throwing demonstrations

---

## 🧪 Testing

### Hardware Sanity Check
```bash
cd backend/tools
python robot_sanity.py  # Test all hardware components
```

### API Contract Tests
```bash
cd backend/tests
pytest test_contract_smoke.py
```

### Backwards Compatibility Test
```bash
cd backend
python test_backwards_compat.py
```

### Model Inference Test
```bash
python test_pickup_ball.py  # Test ACT model endpoint
```

---

## 🔧 Development Tools

### Port Checking
```bash
python backend/tools/check_ports.py          # List available serial ports
python backend/tools/find_so101_port.py      # Locate SO-100 robot
```

### Hardware Verification
```bash
python backend/tools/check_scservo.py        # Test servo communication
python backend/tools/check_torch.py          # Verify PyTorch installation
python backend/tools/verify_arm64_gpu.py     # Check ARM64 GPU (DirectML)
```

### Configuration Check
```bash
python backend/tools/check_config.py         # Validate .env configuration
```

---

## 🌳 Branch Strategy

### Active Branches
- **main**: Stable releases and documentation
- **backend**: Primary development branch (ACT model + full features)
- **backend-branch**: Production backend for dataset replay + ACT
- **frontend** (samu/frontend): React frontend development

### Archived Branches
- **act-model-integration**: Initial ACT experiments (merged)
- **pet-training-integration**: Training pipeline (reference)
- **backend-with-replay**: Experimental merge (reference)

---

## 📦 Dependencies

### Core
- `lerobot`: LeRobot framework for ACT policy
- `flask`: Web server
- `opencv-python`: Camera and image processing
- `torch`: PyTorch for model inference
- `numpy`: Numerical operations

### Optional
- `torch-directml`: ARM64 GPU acceleration (Windows on ARM)
- `pyttsx3`: Text-to-speech
- `scservo-sdk`: Feetech servo control

### Development
- `pytest`: Testing framework
- `black`: Code formatting
- `requests`: API testing

---

## 🎓 Model Information

### Pretrained ACT Model
- **Type**: ACT (Action Chunking Transformer)
- **Framework**: LeRobot
- **Location**: `last/pretrained_model/`
- **Files Required**:
  - `model.safetensors` - Model weights
  - `config.json` - Policy configuration
  - `policy_preprocessor.json` - Input preprocessing
  - `policy_postprocessor.json` - Output postprocessing

### Training
See `vla_integration_plan.md` for training new policies with custom datasets.

---

## 🤝 Contributing

### Code Style
- Python: Follow PEP 8, use `black` for formatting
- Comments: Document complex logic and hardware interactions
- Tests: Add tests for new endpoints and features

### Branch Workflow
1. Create feature branch from `backend` or `backend-branch`
2. Make changes and test thoroughly
3. Ensure backwards compatibility (run `test_backwards_compat.py`)
4. Submit PR with clear description

---

## 📝 Known Issues

### Backend Branch Differences
- **backend-branch**: Uses inline dataset replay in Flask endpoint
- **backend**: Uses CommandManager with separate policy methods
- **Compatibility**: `command=0` and `command=1` work the same in both

### Hardware Requirements
- SO-100 Follower arm required for real robot testing
- USB connection for robot (typically `/dev/tty.usbmodem*` or `COM*`)
- Camera for ACT model inference

### Platform Notes
- **Windows ARM64**: Use `torch-directml` for GPU acceleration
- **Linux**: Standard CUDA or CPU
- **macOS**: CPU only (MPS not supported by LeRobot)

---

## 📞 Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review API documentation in `API_DOCUMENTATION.md`
3. Run diagnostic tools in `backend/tools/`
4. Check contract tests in `contracts/fixtures/`

---

## 📜 License

[Add your license here]

---

## 🙏 Acknowledgments

- **LeRobot Team**: For the ACT policy implementation
- **HuggingFace**: Dataset hosting
- **Feetech**: SO-100 robotic arm

---

**Last Updated**: October 26, 2025  
**Project Status**: 🚀 Active Development  
**Hackathon Ready**: ✅ Yes
