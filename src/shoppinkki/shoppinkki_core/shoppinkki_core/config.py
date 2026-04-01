"""ShopPinkki runtime configuration constants."""

TRACKING_MODE = 'PERSON'        # 'PERSON' | 'ARUCO'
SEARCH_TIMEOUT = 30.0           # searching state timeout (s)
WAITING_TIMEOUT = 300.0         # waiting state timeout (s)
ITEM_ADDING_TIMEOUT = 30.0      # QR scan inactivity timeout (s)
N_MISS_FRAMES = 30              # consecutive miss frames to declare owner_lost
MIN_DIST = 0.25                 # RPLiDAR obstacle minimum distance (m)
REID_THRESHOLD = 0.6            # ReID matching threshold (0~1)

TARGET_AREA = 40000             # PERSON mode target bbox area (px²)
TARGET_DIST_M = 0.8             # ARUCO mode target follow distance (m)
IMAGE_WIDTH = 640               # camera horizontal resolution (px)

KP_ANGLE = 0.002                # P-Control angular gain (common)
KP_DIST_PERSON = 0.0001         # P-Control linear gain — PERSON mode (px² unit)
KP_DIST_ARUCO = 0.5             # P-Control linear gain — ARUCO mode (m unit)

LINEAR_X_MAX = 0.3              # max forward linear velocity (m/s)
LINEAR_X_MIN = -0.15            # max backward linear velocity (m/s)
ANGULAR_Z_MAX = 1.0             # max angular velocity (rad/s)

BATTERY_THRESHOLD = 20          # battery alarm threshold (%)
ALARM_DISMISS_PIN = '1234'      # demo alarm dismiss PIN
