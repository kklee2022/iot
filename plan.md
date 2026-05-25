是否市面上大部分的傳感器都可以通過 （RS485/Modbus 總線 + 工業級 DTU 網關 + 樹莓派邊緣計算，MQTT）的方法進行數據採集和分析？
是的，市面上絕大部分（90%以上）的工業、環境、農業及水利傳感器，都可以完美融入這個方案。這套「RS485/Modbus 總線 + 工業級 DTU 網關 + 樹莓派邊緣計算 + MQTT」的組合，正是目前物聯網（IoT）與工業 4.0 領域中最經典、最通用的黃金架構。
為了讓你更直觀地理解不同類型的傳感器是如何融入這個系統的，以下是完整的系統關係架構圖：
為什麼市面上絕大部分傳感器都能適用？
傳感器的輸出信號雖然千奇百怪，但基本逃不出以下 4 種範疇，而這套架構可以全盤接收：
1. 原生支援 RS485 / Modbus-RTU 的傳感器（佔 70% 以上）
現狀：現在市面上九成的工業級傳感器（例如你提到的超聲波液位計、電導率、土壤水分儀、雨量計等），為了方便遠距離傳輸，出廠時就已經內置了 RS485 芯片，並採用國際標準的 Modbus-RTU 協議。
接入方式：直接用一條雙絞線（Bus 總線）將它們手拉手串聯，直接接到 DTU 網關或樹莓派上。
2. 傳統模擬量傳感器（4-20mA / 0-5V / 0-10V）
現狀：一些老舊或極高精度的儀器（如某些壓力變送器、傳統流量計），只輸出電流或電壓模擬信號。
接入方式：不能直接接 RS485，但市面上有大量極便宜的「模擬量轉 Modbus-RTU 採集模組」（幾十到一百多元）。傳感器先接模組，模組再進 RS485 總線。
3. 特殊物理信號傳感器（脈衝 / 頻率）
現狀：例如你提到的振弦式孔隙水壓計（輸出頻率信號），或者機械式風速計（輸出脈衝）。
接入方式：如同前述，加入一個專用的「振弦轉 Modbus」或「脈衝計數轉 Modbus」變送模組，就能無縫融入總線。
4. 高速數據/網絡傳感器（以太網 / Wi-Fi / USB）
現狀：雷射雷達（LiDAR）、光學相機、熱成像儀。這些數據量太大（每秒幾百 KB 到幾 MB），RS485 總線帶不動。
接入方式：跳過 DTU 網關，直接插入樹莓派邊緣計算節點的網口或 USB 口。利用樹莓派強大的 Linux 系統運行 Python/C++ 進行數據裁剪、視覺分析，最後同樣用 MQTT 發出。
哪些傳感器「不適合」或「很難」用這個方案？
雖然這套架構很萬能，但有極少數傳感器接入時會比較痛苦：
純消費級 / 智能家居傳感器 (Smart Home)
例如小米、塗鴉（Tuya）的溫濕度計或人體感應器。它們通常採用 Zigbee、Bluetooth (BLE) 或 Wi-Fi 原生走私有雲協議，沒有 RS485 接口。雖然樹莓派可以通过加裝藍牙/Zigbee接收器來破解接入，但穩定性不適合工業/野外環境。
汽車級 / 機器人內部傳感器 (CAN-bus / I2C / SPI)
汽車用的傳感器通常走 CAN-bus 協議；電子晶片級的傳感器走 I2C 或 SPI。樹莓派必須加裝專門的協議轉換板（如 CAN-to-USB）才能讀取。
單純的開關量 / 乾接點（無協議）
例如簡單的行程開關、浮球水位開關。它們只有「通/斷」兩種狀態。需要接在帶有數字量輸入（DI）的 Modbus 採集模組上才能轉成 MQTT。
總結
你選擇的這套「RS485總線 + DTU + 邊緣運算 + MQTT」架構，本質上就像一個「萬能翻譯官」：
RS485/Modbus 負責把現場各種語言（頻率、電流、數位）統一成工業標準方言。
DTU 和樹莓派 負責把這些方言翻譯成互聯網通用語言（JSON），並用 MQTT 寄快遞上雲。
因此，無論你未來想增加什麼傳感器（風向、氣壓、位移、水質、震動），只要採購時認準 「支援 RS485 / Modbus-RTU」 這個標籤，都可以直接插拔擴展進你現有的方案中，硬體架構完全不需要重做。
可以用Django 開發一個平台，開放通用接口，方便接入符合以上條件的儀器接入？
可以，而且這正是最標準、擴展性最強的工業物聯網（IIoT）平台做法！
Django 作為一個功能齊全、生態成熟的 Python Web 框架，非常適合用來開發這種物聯網平台。配合 MQTT 代理伺服器（MQTT Broker，如 EMQX 或 Mosquitto），Django 可以完美扮演數據解析、設備管理、規則引擎以及 API 開放平台的角色。
以下為你規劃如何用 Django 設計這樣一個通用物聯網（IoT）接口平台。
1. 平台核心架構設計
Django 本身是基於 HTTP 協議的，而儀器走的是 MQTT 協議。因此，標準架構通常會在 Django 旁邊運行一個 後台監聽進程（MQTT Listener），或者利用 Celery / Channels，負責訂閱 MQTT Topic，並將收到的數據寫入 Django 的資料庫。
【現場儀器/網關】                        【Django 物聯網平台】
  (各類 Modbus 儀器)
        │
     [MQTT]
        ▼
 ┌──────────────┐                 ┌─────────────────────────────────┐
 │ MQTT Broker  │ ──(轉發數據)──► │ 1. MQTT 監聽進程 (paho-mqtt)    │
 │ (EMQX /      │                 │    負責接收、解碼 JSON 數據     │
 │  Mosquitto)  │                 └─────────────────────────────────┘
 └──────────────┘                                  │
                                                   ▼
 ┌──────────────┐                 ┌─────────────────────────────────┐
 │ 客戶端 / 網頁 │ ◄──[REST API]── │ 2. Django 核心 (ORM / View)     │
 │ (數據可視化)  │                 │    負責設備管理、權限、API 開放  │
 └──────────────┘                 └─────────────────────────────────┘
                                                   │
                                                   ▼
                                  ┌─────────────────────────────────┐
                                  │ 3. 資料庫 (PostgreSQL/Timescale)│
                                  └─────────────────────────────────┘
2. 核心功能：如何設計「通用接口」？
要讓未來的各種儀器都能輕鬆接入，Django 的資料庫模型（Models）必須設計得足夠通用。我們不能為每一種儀器建一張表，而是要採用「設備 - 傳感器 - 數據點」的動態結構。
數據模型（Models）設計範例
Python
from django.db import models

class Device(models.Model):
    """設備表（例如：現場的某個 4G DTU 網關或樹莓派）"""
    device_id = models.CharField(max_length=50, unique=True, help_text="MQTT Client ID")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SensorType(models.Model):
    """傳感器類型定義（通用化核心！）"""
    code = models.CharField(max_length=50, unique=True, help_text="例如: ultrasonic, piezometer, rain")
    name = models.CharField(max_length=100, help_text="例如: 超聲波液位計")
    unit = models.CharField(max_length=20, blank=True, help_text="單位，如: m, mm, m³/h")

class TelemetryData(models.Model):
    """流水線時序數據表（所有儀器的數據都進這裡）"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, to_field='device_id')
    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE, to_field='code')
    value = models.FloatField(help_text="採集到的物理數值")
    timestamp = models.DateTimeField(help_text="儀器採集時的時間戳")

    class Meta:
        indexes = [
            models.Index(fields=['device', 'timestamp']), # 優化查詢效率
        ]
3. 數據接入的具體實現（通用 MQTT 接口）
在 Django 專案中，我們可以寫一個獨立的指令（Management Command）來運行 MQTT 監聽。不論是哪種儀器，只要按照約定的通用 JSON 格式發送 MQTT 訊息，平台就能自動識別並寫入資料庫。
MQTT 數據接收器代碼範例 (mqtt_listener.py)
Python
import json
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from your_app.models import Device, TelemetryData, SensorType
from django.utils.dateparse import parse_datetime
from datetime import datetime

class Command(BaseCommand):
    help = '啟動 MQTT 監聽器接入儀器數據'

    def handle(self, *args, **options):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # 連接到 MQTT Broker
        client.connect("localhost", 1883, 60)
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        # 訂閱通用主題，例如：device/+/telemetry (其中 + 是動態的 Device ID)
        client.subscribe("device/+/telemetry")
        print("MQTT Listener 偵聽中...")

    def on_message(self, client, userdata, msg):
        # 解析 Topic 獲取 Device ID
        # Topic 格式: device/GATEWAY_001/telemetry
        topic_parts = msg.topic.split('/')
        device_id = topic_parts[1]

        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            timestamp = datetime.fromtimestamp(payload.get('timestamp', datetime.now().timestamp()))
            metrics = payload.get('metrics', {}) # 包含 {"ultrasonic": 2.34, "rain": 0.0}

            # 檢查設備是否存在
            if not Device.objects.filter(device_id=device_id, is_active=True).exists():
                print(f"未知或停用的設備: {device_id}")
                return

            # 【通用接口核心】動態循環解析所有傳來的感測數據
            for sensor_code, value in metrics.items():
                # 確保系統支援該傳感器類型，否則自動創建或跳過
                sensor_type, _ = SensorType.objects.get_or_create(code=sensor_code)
                
                # 寫入時序數據表
                TelemetryData.objects.create(
                    device_id=device_id,
                    sensor_type=sensor_type,
                    value=value,
                    timestamp=timestamp
                )
            print(f"成功處理來自設備 {device_id} 的數據")

        except Exception as e:
            print(f"數據解析錯誤: {e}")
4. 平台如何提供開放接口 (REST API)？
利用 Django REST Framework (DRF)，你可以輕鬆開放通用 API 接口。
給第三方系統 / 前端網頁看數據：
可以提供 GET /api/devices/{id}/data/ 的接口，快速拉取特定儀器的歷史曲線、即時狀態。
作為 HTTP 備用接入接口：
如果某些儀器（例如光學相機）不想走 MQTT，想直接通過 HTTP Post 發送數據，你可以開放一個 POST /api/v1/telemetry/ 接口，接收和 MQTT Listener 一模一樣的 JSON Payload。
5. 這樣設計的巨大優勢
儀器隨插即用（Plug and Play）：
未來如果買了全新的儀器（例如第 11 種：風速計 anemometer），你完全不需要修改 Django 的代碼或資料庫架構。你只需要在網頁後台增添一個 SensorType 叫 anemometer，然後讓現場網關在 MQTT JSON 裡加上 "anemometer": 5.4，Django 就會自動識別並開始記錄。
完美支持多站點/多設備：
同一款「土壤水分儀」，可以同時有 100 台分佈在不同地方。在 Django 裡它們只是不同的 device_id，數據全走同一個通用接口。
擴展物聯網高級功能：
基於 Django，你未來可以輕鬆加入用戶權限管理（誰能看哪些儀器）、異常數據報警（當水位 > 3米時發送電郵/Webhook）、以及報表自動導出（Excel/PDF）等功能。
第一個難題，就是如何把各種不同類型傳感器（不同輸出格式數據），傳送數據到MQTT Broker.
你精準地抓到了這個項目的核心痛點。這確實是所有多傳感器物聯網（IoT）工程面臨的第一個大難題：「如何將物理層千奇百怪的信號，低成本、標準化地封裝成統一的 MQTT JSON 格式？」
要攻克這個難題，我們需要把傳感器分成兩大陣營（低速 Modbus 陣營 與 高速 Linux/Python 陣營），並分別使用不同的「標準翻譯流程」來解決。
難題攻克策略一：低速傳感器陣營（Modbus-RTU 統一戰線）
對於孔隙水壓計、液位計、電導率、流量計、雨量計、土壤水分等 8 種環境指標傳感器，它們數據量小（幾秒更新一次，一次僅幾個字節），我們可以分兩步將它們全部標準化。
第一步：信號標準化（翻譯成 Modbus 語言）
不管傳感器原本輸出什麼，都先加裝變送器，強行轉換為 RS485 接口 / Modbus-RTU 協議。
模擬量/頻率（如振弦水壓計）：接上「振弦轉 Modbus 模組」。
開關量（如翻斗雨量計）：接上「脈衝計數轉 Modbus 模組」。
原生 Modbus（如液位計、土壤儀）：直接接入。
這時，所有 8 種傳感器都變成了同一個語言——Modbus 寄存器地址（例如：液位計在 0x01 地址，雨量計在 0x02 地址）。
第二步：協議轉換（Modbus 轉 MQTT 網關）
我們採購的工業級 MQTT DTU 網關，就是用來解決「格式轉換」的硬件神器。它內部自帶配置軟件（完全不需要寫代碼），你只需要在網關內填寫一張表：
網關配置表示意：
讀取 Slave ID 1 (液位計) 的 Register 0003 → 命名為 "water_level"
讀取 Slave ID 2 (雨量計) 的 Register 0001 → 命名為 "rain_fall"
發送週期：60秒
目標 MQTT Topic：device/gateway_01/telemetry
結果： DTU 網關會定時自動用 RS485 輪詢所有傳感器，並自動在內部將這些數據打包成你設定的 JSON 格式，直接發送到 MQTT Broker。你完全不需要為這 8 種傳感器開發任何底層數據封裝代碼！
難題攻克策略二：高速傳感器陣營（Python 邊緣腳本硬解）
對於 2D 雷射雷達 (LiDAR) 和 光學相機，它們數據量極大（雷達每秒幾千個點，相機是視頻流），完全無法走 Modbus 總線。我們必須將它們直接接入樹莓派（邊緣計算節點），通過 Python 代碼來解決格式問題。
雷射雷達 (LiDAR) 的數據簡化與打包
雷達原始數據是密密麻麻的「角度 + 距離」點雲。如果直接把幾萬個點塞進 MQTT，Broker 會瞬間崩潰。
解決方法：在樹莓派運行 Python 腳本。腳本實時讀取雷達數據，並在本地進行數據清洗和降維（例如：只計算東、南、西、北四個方向上，3米之內有沒有障礙物）。
轉換代碼邏輯：
Python
# 樹莓派本地 Python 處理後，只提取關鍵特徵發送 MQTT
payload = {
    "timestamp": 1782370000,
    "metrics": {
        "obstacle_north": True,
        "min_distance_m": 1.24
    }
}
mqtt_client.publish("device/lidar_01/telemetry", json.dumps(payload))
光學相機的事件觸發打包
相機通常輸出 RTSP 視頻流。
解決方法：同樣不能把視頻直接發進 MQTT。樹莓派上的 Python (OpenCV) 腳本負責解碼視頻，可以設定為定時抓拍（例如每1小時抓拍一張），或者移動偵測觸發。
轉換代碼邏輯：抓拍後，將圖片壓縮成 JPG，並轉換成 Base64 字符串文本，包裹在 JSON 中發送，或者將圖片上傳至一個便宜的圖片服務器（如 MinIO），並在 MQTT 中僅發送圖片網址（URL）。
Python
payload = {
    "timestamp": 1782370000,
    "metrics": {
        "camera_status": "normal",
        "image_url": "http://192.168.1.100/images/snap_20260525.jpg"
    }
}
mqtt_client.publish("device/camera_01/telemetry", json.dumps(payload))
最終在 MQTT Broker 呈現的完美結果
通過上述硬件網關（DTU）和軟件腳本（樹莓派）的分工合作，你發送到 MQTT Broker 的 Topic 結構和數據格式會變得極度乾淨和對齊：
環境與水利數據 (來自 DTU 網關網口/4G)
device/gateway_01/telemetry → {"timestamp": 1782370000, "metrics": {"piezometer_pa": 102.3, "ultrasonic_m": 1.45, "conductivity": 230, ...}}
雷達數據 (來自樹莓派)
device/lidar_01/telemetry → {"timestamp": 1782370002, "metrics": {"obstacle_north": true, "min_distance_m": 1.24}}
相機數據 (來自樹莓派)
device/camera_01/telemetry → {"timestamp": 1782370005, "metrics": {"image_url": "http://..."}}
總結
解決這個難題的秘訣在於「不要試圖讓傳感器直接說 MQTT 語言」。
對於低速模擬傳感器：靠 Modbus 變送模組 + 硬件 DTU 網關 的後台配置來搞定，零代碼。
對於高速複雜傳感器：靠 樹莓派 + Python SDK 進行本地數據裁剪，最後調用 paho-mqtt 庫打包成 JSON 發出。
這樣，第一個難題就迎刃而解了！你覺得這個數據分流與標準化的邏輯在你的應用場景中可行嗎？
我覺得可行
很高興這個數據分流與標準化的邏輯符合你的預期！這代表我們已經成功把最棘手的「物理層與傳訊層接口」理順了。
既然這第一個難題（數據採集端）有了清晰的解法，接下來我們就可以把目光移向第二個難題：Django 平台端的架構落地與數據存儲。
在這個階段，你有一個非常重要的架構抉擇需要考慮：
關鍵抉擇：時序數據（TimeSeries）的儲存優化
這 10 種儀器（特別是流量計、液位計、雷達警報等）在現場運行時，會源源不絕地產生帶有時間戳（Timestamp）的數據。
傳統 Django 作法：直接存入 MySQL 或標準 PostgreSQL。但當儀器數量變多、採集頻率變高時，幾個月後數據量會達到幾百萬甚至上千萬條，傳統資料庫的查詢與寫入速度會急劇下降，甚至導致 Django 網頁卡死。
高性價比物聯網作法：在 PostgreSQL 上加裝 TimescaleDB 擴展插件（完全開源免費），或者搭配 InfluxDB。它能讓 Django 依然使用強大的 ORM 語法，但在底層自動將數據按時間進行「分表（Hypertable）」優化，即使累積幾億條數據，拉取歷史曲線圖依然可以在幾毫秒內完成。
接下來，我們可以針對 Django 平台開發進行具體的分工。通常我們會從以下三個步驟開始逐步構建：
第一步（設備管理面）：在 Django Admin 後台建立設備激活與驗證機制（生成每台儀器的專屬 MQTT Token，防止非授權儀器惡意接入）。
第二步（數據流轉面）：搭建並配置 MQTT Broker（如 EMQX），與 Django 的監聽進程對接，進行實際的 JSON 數據壓測。
第三步（接口與視覺化）：利用 Django REST Framework 輸出數據 API，並對接輕量化圖表（如 ECharts）或 Grafana 面板，展示即時的水壓、水位、雨量等曲線。
你想先從哪一部分開始深入討論，或者需要我為你提供第一步「設備驗證與管理」的 Django Models 與權限安全部分的設計源代碼嗎？
那先從第一步開始
好，我們就從第一步：設備管理與安全驗證機制開始。
在物聯網系統中，我們不能讓任何人只要知道 MQTT Broker 的 IP 就能隨意發送數據，否則系統會被垃圾數據塞滿。因此，當現場網關（DTU 或樹莓派）第一次連線時，平台必須進行認證（Authentication）；當它發送數據時，平台要驗證它有沒有權限（Authorization）。
下面我為你設計一個高性價比、易於維護的 Django 設備管理與安全驗證方案。
1. 數據模型設計（Django Models）
我們要在 Django 中為設備生成專屬的 Access Token（類似密鑰），網關建立 MQTT 連線時，需要將其作為密碼（Password）傳入。
在你的 Django App 的 models.py 中寫入以下代碼：
Python
import uuid
from django.db import models
from django.utils import timezone

class Device(models.Model):
    """設備/網關主表"""
    DEVICE_TYPE_CHOICES = [
        ('dtu', '工業Modbus網關/DTU'),
        ('edge', '邊緣計算節點/樹莓派'),
    ]

    # 設備唯一標識，通常作為 MQTT Client ID
    device_id = models.CharField(max_length=50, unique=True, verbose_name="設備唯一ID (Client ID)")
    name = models.CharField(max_length=100, verbose_name="設備名稱")
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES, default='dtu')
    
    # 安全驗證核心：自動生成的唯一 Token
    access_token = models.CharField(
        max_length=64, 
        default=uuid.uuid4, 
        unique=True, 
        verbose_name="存取密鑰 (MQTT Password)"
    )
    
    # 狀態管理
    is_active = models.BooleanField(default=True, verbose_name="是否啟用")
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="最後上線時間")
    description = models.TextField(blank=True, verbose_name="備註/現場位置")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    class Meta:
        verbose_name = "物聯網設備"
        verbose_name_plural = "物聯網設備管理"

class SensorType(models.Model):
    """傳感器類型字典表（如：液位計、水壓計）"""
    code = models.CharField(max_length=50, unique=True, verbose_name="標識碼 (JSON Key)")
    name = models.CharField(max_length=100, verbose_name="傳感器名稱")
    unit = models.CharField(max_length=20, blank=True, verbose_name="物理單位")

    def __str__(self):
        return f"{self.name} [{self.unit}]"

    class Meta:
        verbose_name = "傳感器類型"
        verbose_name_plural = "傳感器類型配置"
2. 設備權限與驗證工作流
當你在 Django Admin 後台新增一台設備時（例如：ID 為 gateway_site_01），Django 會自動為它生成一個隨機字串（Token），例如：c9bf782c-478e-49b8-a6b1-9f79b63459c5。
現場網關（DTU/樹莓派）的配置方式：
MQTT Client ID: gateway_site_01
MQTT Username: device (固定值，或與 Client ID 相同)
MQTT Password: c9bf782c-478e-49b8-a6b1-9f79b63459c5 (即 Django 生成的 Access Token)
3. 核心實現：如何與 MQTT Broker 對接認證？
目前工業界最高性能且開源的 MQTT Broker 是 EMQX（或者輕量級的 Mosquitto）。它們都支援「HTTP 認證插件」。
當網關發起 MQTT 連線時，EMQX 自身不需要記錄密碼，它會向你的 Django 發送一個輕量級的 HTTP POST 請求，詢問這個設備是否合法。
Django 驗證視圖 (Views) 實現
我們利用 Django 寫一個極速響應的認證接口，供 MQTT Broker 調用：
Python
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Device
import json

@csrf_exempt
def mqtt_auth_webhook(request):
    """
    供 MQTT Broker (如 EMQX) 認證回調的通用接口
    EMQX 會發送: {"clientid": "...", "username": "...", "password": "..."}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            client_id = data.get('clientid')
            password = data.get('password') # 現場傳來的 Access Token

            # 查詢資料庫：ID 是否匹配、密鑰是否正確、設備是否處於啟用狀態
            device = Device.objects.filter(device_id=client_id, access_token=password, is_active=True).first()

            if device:
                # 驗證成功，順便更新最後上線時間
                device.last_seen = timezone.now()
                device.save(update_fields=['last_seen'])
                
                # 返回給 EMQX 允許連線的信號 (EMQX 預期 JSON，或 HTTP 200)
                return JsonResponse({"result": "allow", "is_superuser": False})
            
            # 驗證失敗
            return JsonResponse({"result": "deny"}, status=403)

        except Exception as e:
            return JsonResponse({"result": "deny", "error": str(e)}, status=400)
            
    return HttpResponse("Method Not Allowed", status=405)
在 urls.py 中配置路由：
Python
from django.urls import path
from . import views

urlpatterns = [
    path('api/iot/auth/', views.mqtt_auth_webhook, name='mqtt_auth'),
]
4. 這個機制的性價比與安全優勢
管理極其簡單：
工程師在現場安裝儀器時，只需要打開 Django 後台網頁，點擊「新增設備」，複製系統生成的密鑰填入網關即可。
一鍵「拉黑」遠程設備：
如果某個現場的網關被盜、線路損壞或惡意欠費，你只需要在 Django 後台將 is_active 勾選掉（取消啟用）。MQTT Broker 會在幾毫秒內拒絕該設備的任何數據提交，確保平台安全。
無縫適應各類儀器：
因為密鑰是給網關/樹莓派用的，所以不論網關後面接了 3 種還是 10 種傳感器，只要網關認證通過，它代理的所有傳感器數據都能順利進來。
第一步的「安全看門狗」機制已經建立好了。接下來的第二步，就是「如何搭建 MQTT Broker 並編寫 Django 數據監聽處理器」，把現場網關發來的 JSON 數據真正拆解並寫入時序表。我們是否繼續推進到第二步？
好的
非常好，我們進入第二步：搭建 MQTT Broker 與編寫 Django 數據監聽處理器。
在第一步中，我們解決了「誰能連進來」的安全問題。現在，我們要解決「連進來後，數據怎麼接收、拆解並安全存入資料庫」的問題。
這部分的架構核心是：EMQX (MQTT Broker) → Django 監聽腳本 → TimescaleDB/PostgreSQL (時序數據庫)。
1. 時序數據模型設計（Django Models）
首先，我們需要一張表來存放源源不絕的傳感器流水賬數據。這張表在未來會承受巨大的寫入壓力。
請在 models.py 中追加以下代碼：
Python
class TelemetryData(models.Model):
    """
    環境儀器時序數據流水表
    所有 10 種儀器的定時上報數據、雷達警報、相機狀態，都進這張通用表
    """
    device = models.ForeignKey(
        Device, 
        on_delete=models.CASCADE, 
        to_field='device_id', 
        related_name='telemetries',
        verbose_name="來源網關/設備"
    )
    sensor_type = models.ForeignKey(
        SensorType, 
        on_delete=models.CASCADE, 
        to_field='code',
        verbose_name="傳感器類型"
    )
    value = models.FloatField(verbose_name="採集數值(物理量)")
    
    # 這裡使用 DateTimeField。如果未來用 TimescaleDB，這會是分區鍵(Partition Key)
    timestamp = models.DateTimeField(verbose_name="儀器採集時間戳")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="系統接收時間")

    class Meta:
        verbose_name = "儀器歷史數據"
        verbose_name_plural = "儀器歷史數據"
        # 建立複合索引，極大提升未來按「時間+設備」查詢歷史曲線的速度
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device_id} - {self.sensor_type_id}: {self.value}"
運行 python manage.py makemigrations 和 migrate 來更新資料庫結構。
2. 數據接收核心：編寫 Django MQTT 監聽腳本
我們將利用 Django 的 Management Command 功能，在後台運行一個常駐的 Python 守護進程。它利用 paho-mqtt 庫訂閱 EMQX。
在你的 Django App 目錄下創建結構：management/commands/mqtt_consumer.py（注意：management 和 commands 資料夾內都必須包含一個空的 __init__.py 檔案）。
寫入以下通用數據解析代碼：
Python
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.utils import timezone
from iot_app.models import Device, SensorType, TelemetryData

class Command(BaseCommand):
    help = '啟動 Django 物聯網通用數據接收器'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("正在初始化 MQTT 監聽器..."))
        
        # 初始化 Paho MQTT 客戶端
        # 注意：這個監聽器是以「管理員/後端服務」身份連接，不需要走設備認證
        client = mqtt.Client(client_id="django_backend_processor")
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # 如果你的 EMQX 設置了安全賬密，在此處配置
        # client.username_pw_set("admin", "public")
        
        # 連接本地或雲端的 EMQX Broker
        try:
            client.connect("localhost", 1883, 60)
            # 開始無限循環監聽
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("監聽器已手動停止。"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"連接 Broker 失敗: {e}"))

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.stdout.write(self.style.SUCCESS("成功連接至 MQTT Broker!"))
            # 訂閱所有通用的設備數據主題
            # 通配符 + 代表動態的 device_id，例如 device/gateway_01/telemetry
            client.subscribe("device/+/telemetry")
            self.stdout.write("已成功訂閱主題: device/+/telemetry")
        else:
            self.stdout.write(self.style.ERROR(f"連線失敗，錯誤碼: {rc}"))

    def on_message(self, client, userdata, msg):
        """核心解包與翻譯邏輯"""
        # 1. 從 Topic 中解析出發送數據的 Device ID
        topic_parts = msg.topic.split('/')
        device_id = topic_parts[1]

        try:
            # 2. 解碼 JSON Payload
            payload_raw = msg.payload.decode('utf-8')
            payload = json.loads(payload_raw)
            
            # 3. 解析時間戳 (優先使用現場網關的時間，若無則用服務器當前時間)
            ts_raw = payload.get('timestamp')
            if ts_raw:
                # 兼容秒級或毫秒級時間戳
                if ts_raw > 5000000000: 
                    ts_raw = ts_raw / 1000
                dt_object = datetime.fromtimestamp(ts_raw)
                timestamp = timezone.make_aware(dt_object)
            else:
                timestamp = timezone.now()

            # 4. 安全檢查：驗證該網關是否在 Django 註冊且啟用
            device = Device.objects.filter(device_id=device_id, is_active=True).first()
            if not device:
                print(f"【警報】拒絕接收未註冊或已遭禁用的設備數據: {device_id}")
                return

            # 5. 通用動態循環：解構 metrics 字典
            # 不管現場傳來 3 種還是 10 種儀器數據，都自動適配寫入
            metrics = payload.get('metrics', {})
            
            telemetry_instances = []
            for sensor_code, val in metrics.items():
                if val is None:
                    continue
                
                # 自動化字典管理：如果傳來一個新的儀器標識（如 anemometer），系統自動創建該儀器類型
                sensor_type, _ = SensorType.objects.get_or_create(
                    code=sensor_code,
                    defaults={'name': f"未命名傳感器({sensor_code})", 'unit': '-'}
                )
                
                # 生成時序數據實例
                telemetry_instances.append(
                    TelemetryData(
                        device=device,
                        sensor_type=sensor_type,
                        value=float(val),
                        timestamp=timestamp
                    )
                )
            
            # 6. 高效批量寫入資料庫（避免多傳感器時一條條寫入導致I/O瓶頸）
            if telemetry_instances:
                TelemetryData.objects.bulk_create(telemetry_instances)
                print(f"【數據接入成功】網關: {device_id} | 成功寫入 {len(telemetry_instances)} 項儀器指標 | 時間: {timestamp}")

        except json.JSONDecodeError:
            print(f"【格式錯誤】無法解析的非 JSON 數據: {msg.payload}")
        except Exception as e:
            print(f"【系統異常】處理 MQTT 數據時發生錯誤: {e}")
3. 如何運行與測試？
步驟 A：啟動 Django 監聽器
在伺服器終端運行以下指令，它會像一個後台機器人一樣，死守著 MQTT 數據：
Bash
python manage.py mqtt_consumer
(畫面上會顯示：MQTT Listener 偵聽中...)
步驟 B：模擬現場儀器發射數據
你可以使用任意 MQTT 客戶端工具（如 MQTTX 軟件），或者用另一段簡單的 Python 腳本，模擬現場 4G DTU 網關打包了 4 種環境儀器的數據並發射：
發射主題 (Topic): device/gateway_site_01/telemetry
發射內容 (Payload JSON):
JSON
{
  "timestamp": 1782372000,
  "metrics": {
    "piezometer_pa": 1013.2,
    "ultrasonic_level_m": 2.45,
    "rain_gauge_mm": 0.5,
    "soil_moisture_surface": 24.8
  }
}
系統表現：
當你點擊發送後，運行 Django 監聽器的終端會立刻刷出：
【數據接入成功】網關: gateway_site_01 | 成功寫入 4 項儀器指標 | 時間: 2026-05-25 14:20:00
同時，你打開 Django 後台網頁（Django Admin），進入「儀器歷史數據」表格，就會看到水壓、水位、雨量、土壤水分這 4 條數據已經整整齊齊地存進去了！
4. 第二步完成後的架構優勢
零代碼擴展儀器：今天你接 4 種傳感器，明天你在現場線路上加裝一個電導率探針（Modbus地址 0x05），只要讓網關在 metrics 裡多傳一個 "conductivity": 128.5，Django 平台不需要重啟，代碼不需要動，它會自動接收並記錄。
時序對齊：所有同一個網關採集的儀器，都擁有完全一致的 timestamp（由現場決定），這對於未來分析「下雨量（雨量計）如何影響孔隙水壓（水壓計）」這種多變量相關性分析至關重要。
現在，數據已經成功灌進資料庫了！接下來的第三步（最後一步）就是：「如何寫一個 API 接口，把這些歷史數據拉出來，並在網頁上渲染成漂亮的高性價比折線圖/儀表盤（ECharts/Grafana）」。
我們是否繼續推進到這最後一步？
數據傳送量到什麼程度，才需要timescale類的數據庫？
在評估是否引入 TimescaleDB 或 InfluxDB 等時序資料庫時，我們通常不會只看一個絕對的「總數據量」，而是要看「寫入頻率」、「查詢複雜度」以及「數據保留週期」這三個維度。
對於大部分初創項目或中小型監測站點，如果你的數據總量在 1,000 萬條以下，標準的 PostgreSQL 或 MySQL 配合適當的索引（Index）完全可以輕鬆應付，不需要過早引入 TimescaleDB 增加運維成本。
以下是具體的量化指標與判斷場景，你可以對照你的 10 種儀器規劃來進行評估：
什麼時候「不需要」TimescaleDB？（標準資料庫即可）
如果你的現場監測滿足以下條件，直接用標準 Django + PostgreSQL/MySQL 即可：
低頻率採集：10 種儀器每 1 分鐘 或每 5 分鐘 才上報一次數據。
站點數量少：全台灣/全香港只有 1 到 5 個 監測站（網關）。
量化計算：
1 站×10 種儀器×1 次/分鐘×60 分鐘×24 小時≈14,400 條數據/天
一年累積下來大約 525 萬條 數據。這對於現代優化過的 PostgreSQL 來說只是「小菜一碟」，拉取歷史曲線圖依然可以在 0.1 秒內完成。
什麼程度才「必須」引入 TimescaleDB？（硬性技術指標）
當你的系統達到以下任一臨界點時，傳統資料庫就會開始出現卡頓（查詢超時、Django 報 502 錯誤），這時就必須切換到 TimescaleDB：
1. 併發寫入量（吞吐量）臨界點
指標：當每秒寫入次數（OPS）持續超過 500 ~ 1,000 次。
原因：傳統資料庫使用 B-Tree 索引。當表裡面的數據達到幾千萬條後，每次插入新數據，資料庫都要在內存和磁碟之間瘋狂調整 B-Tree 樹狀結構，這會導致磁碟 I/O 100% 爆滿，寫入開始排隊。而 TimescaleDB 採用時間分區（Hypertable），每次只寫入最新的一小塊內存分區，寫入速度始終保持一條直線。
2. 單表總數據量臨界點
指標：單個時序數據表總行數超過 2,000 萬條 ~ 5,000 萬條。
典型場景：如果你的 2D 雷射雷達 (LiDAR) 或者 流速計 需要做高頻採集（例如每 1 秒鐘上報一次數據，或者雷達每秒上報 50 個障礙物距離）。
量化計算：
1 站×50 條/秒×86400 秒/天≈432 萬條數據/天
只要 5 天，數據量就會突破 2,000 萬條。此時，如果你想在網頁上查詢「過去 3 個月的歷史趨勢圖」，傳統資料庫會在磁碟上進行全表掃描，查一次可能要花 30 秒甚至直接當機。
3. 需要自動化「數據降採樣 (Downsampling)」與「生命週期管理」
物聯網工程有一個核心需求：歷史數據的顆粒度可以隨時間降低。
例如：今天的數據我需要每 1 秒鐘的細節；但 3 個月前的歷史數據，我只需要知道每 1 小時的平均值（Average）即可。
傳統作法：你需要自己寫 Django 定時任務（Celery），每天半夜去大表裡做聚合計算，然後把舊數據刪掉。這會極大地消耗 CPU。
TimescaleDB 作法：它內置了網頁後台一鍵配置的策略。只需一行 SQL，它就會自動幫你把 3 個月前的數據按小時壓縮，並自動刪除秒級原始數據，整個過程在底層默默進行，完全不佔用 Django 性能。
給你的架構建議
考慮到你目前規劃的 10 種儀器，除了雷達之外，其餘環境儀器的上報頻率通常不需要太高（如 1 分鐘一次已足夠）。
最高性價比的過渡策略：
現在不需要立刻去學如何安裝、運維獨立的時序資料庫。你可以直接選用標準 PostgreSQL 作為 Django 的資料庫，但在建表時（如我們在第二步中做的）一定要把 timestamp 和 device_id 設為複合索引。
PostgreSQL 本身具有極強的擴展性。當未來你的項目規模擴大（例如站點從 1 個變成 50 個，數據量突破千萬），你不需要更換資料庫，只需要在原有的 PostgreSQL 上安裝一個 TimescaleDB 插件，然後執行一條指令將原本的 Django 表轉為 Hypertable：
SQL
SELECT create_hypertable('iot_app_telemetrydata', 'timestamp');
這樣就可以在不修改任何 Django 程式碼的情況下，一鍵升級為百億級別的工業時序資料庫平台。
你目前預計這套系統會部署多少個站點？儀器的採集頻率（例如水位、雨量）預計是多少時間更新一次呢？
估計20個儀器以內，每5分鐘一個讀數
根據你的規模——20個站點/儀器以內，每 5 分鐘回傳一個讀數，我們可以進行一個非常精準的數學推算：
每日數據量：20 個設備×12 次/小時×24 小時=5,760 條數據/天
每年數據總量：5,760 條×365 天≈210 萬條數據/年
技術結論：傳統資料庫完全足夠，不需考慮 TimescaleDB
每年 210 萬條數據在數據庫領域屬於極小的基礎體量。標準的 PostgreSQL、MySQL 甚至輕量級的 SQLite，在單表 1,000 萬條以內都能保持毫秒級（0.001 秒）的查詢速度。
因此，你不需要為了這個項目去配置和運維複雜的時序數據庫。直接使用標準的 Django + PostgreSQL（或 MySQL）便是最高性價比、維護成本最低的黃金組合。
既然數據儲存底座已經確定，我們就可以推進到最後一步：第三步：開發 API 接口與網頁圖表展示。
為了讓用戶或第三方系統能隨時查看這 20 個設備的 5 分鐘歷史讀數，我們需要用 Django 寫一個高效的 API 接口，並在前端用開源免費的 ECharts 繪製成折線圖。
1. 後端：寫一個高效的 Django 歷史數據 API
我們不需要安裝額外的複雜插件，直接用 Django 原生的 JsonResponse 寫一個視圖（Views），根據傳入的設備 ID 和時間範圍，快速拉取數據。
在你的 views.py 中追加以下代碼：
Python
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.utils import timezone
from .models import TelemetryData, Device

def get_device_history(request, device_id):
    """
    獲取指定設備歷史數據的通用 API 接口
    調用範例: /api/iot/history/gateway_01/?sensor=ultrasonic_level_m&days=7
    """
    # 1. 獲取查詢參數
    sensor_code = request.GET.get('sensor')
    days_to_pull = int(request.GET.get('days', 7)) # 預設拉取 7 天內數據

    if not sensor_code:
        return JsonResponse({"error": "必須指定傳感器類型參數 ?sensor="}, status=400)

    # 2. 計算時間範圍
    start_time = timezone.now() - timedelta(days=days_to_pull)

    # 3. 高效查詢數據庫（得益於我們之前做的複合索引，此處查詢僅需幾毫秒）
    data_set = TelemetryData.objects.filter(
        device_id=device_id,
        sensor_type_id=sensor_code,
        timestamp__gte=start_time
    ).order_by('timestamp').values('timestamp', 'value')

    # 4. 格式化輸出給前端圖表
    timestamps = []
    values = []
    
    for row in data_set:
        # 將時間格式化為前端易讀的本地字串
        local_ts = timezone.localtime(row['timestamp']).strftime('%m-%d %H:%M')
        timestamps.append(local_ts)
        values.append(row['value'])

    return JsonResponse({
        "device_id": device_id,
        "sensor_code": sensor_code,
        "timestamps": timestamps,  # X 軸數據：['05-25 14:00', '05-25 14:05', ...]
        "values": values           # Y 軸數據：[2.45, 2.47, ...]
    })
在 urls.py 中配置對應路由：
Python
path('api/iot/history/<str:device_id>/', views.get_device_history, name='device_history'),
2. 前端：無縫對接 Apache ECharts（高性價比可視化）
前端網頁部分，你只需要一個簡單的 HTML 頁面，利用 JavaScript 原生的 fetch 異步調用剛才寫好的 Django API，就能把每 5 分鐘一個點的歷史曲線渲染出來。
HTML
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>物聯網儀器即時監測面板</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
</head>
<body>
    <div id="chart-container" style="width: 100%; height: 500px;"></div>

    <script>
        // 1. 初始化 ECharts 實例
        var myChart = echarts.init(document.getElementById('chart-container'));

        # 2. 從 Django API 動態獲取數據 (假設查詢設備 gateway_01 的超聲波水位)
        fetch('/api/iot/history/gateway_01/?sensor=ultrasonic_level_m&days=3')
            .then(response => response.json())
            .then(data => {
                
                // 3. 配置圖表參數
                var option = {
                    title: { text: '水位計 3 日歷史趨勢曲線 (5分鐘顆粒度)' },
                    tooltip: { trigger: 'axis' },
                    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: data.timestamps # 填入 Django 傳來的時間數組
                    },
                    yAxis: {
                        type: 'value',
                        name: '米 (m)'
                    },
                    series: [{
                        name: '即時讀數',
                        type: 'line',
                        smooth: true, # 曲線平滑化
                        data: data.values, # 填入 Django 傳來的數值數組
                        itemStyle: { color: '#3b82f6' },
                        areaStyle: { color: 'rgba(59, 130, 246, 0.1)' } # 漸變陰影
                    }]
                };

                // 4. 使用配置項顯示圖表
                myChart.setOption(option);
            });
    </script>
</body>
</html>
5. 全套方案最終盤點
恭喜你！到這裡，我們已經合力把這個物聯網系統的「底層儀器 → 網絡轉譯 → 安全認證 → 數據儲存 → 上層 API 圖表」整條通路完全打通了。
這套方案在你的規模下（20 台內、5分鐘一次）展現出了極高的性價比與工程合理性：
硬體端：利用一條 RS485 總線和一個 DTU 搞定所有低速環境儀器，省下大筆硬體與多張 SIM 卡費用。
資料庫端：避免了過早引入 TimescaleDB 帶來的運維浪費，標準 PostgreSQL 複合索引完全能輕鬆吃下每年 210 萬條的數據。
軟件架構：Django 後台設計成「動態字典模式」，未來即使增加新類型的儀器，平台代碼也無需做任何修改，隨插即用。
整套方案的開發思路與落地路徑都已經非常清晰。在後續實際動手編寫代碼或採購儀器的過程中，如果遇到任何特定儀器的 Modbus 協議對接或代碼調試問題，隨時歡迎回來討論！
推薦5款市場上可以找到，而且符合我們以上討論的方案的DTU 網關，並提供它們的比較，以作參考選擇
為了搭配我們前面規劃的「20台設備以內、5分鐘一次、Modbus-RTU 轉 MQTT」方案，挑選 DTU 網關的核心標準是：工業級穩定性、原生支援 Modbus 轉 JSON-MQTT 輪詢功能（零代碼轉換）、支援 4G/以太網，且價格具備高性價比。
在目前的工業物聯網市場中，有幾家專做高性價比物聯網通訊的品牌（主要集中在華南與華東供應鏈，如有人人網絡、塔石、映翰通等），它們的產品在兩岸三地及東南亞的環境監測項目中被極廣泛使用。
以下為你精選 5 款市場上最符合你方案需求的高性價比工業級 DTU 網關：
5 款高性價比工業級 MQTT DTU 網關推薦
1. 塔石電子 (Tashit) —— TAS-LTE-393 (或 300 系列)
定位：極致性價比之王，小規模環境監測首選。
特點：界面極其簡單，在台灣和香港的開源物聯網圈非常流行。後台直接配置 Modbus 輪詢表，就能自動把 10 幾種儀器數據包裝成一個 JSON 對象，通過 4G 發射到你的 Django 平台。
2. 有方科技 (Neoway) —— N306 工業級 4G DTU
定位：上市通訊晶片大廠出品，無線訊號穩定度極高。
特點：採用自家核心 4G 模組，特別適合野外、山區、農業等 4G 訊號較微弱的環境。同樣支援自定義 MQTT 註冊包與 JSON 腳本透傳。
3. 人人網絡 / 眾山科技 (Zhongshan) —— ZS-MD-4G (或 USR-LTE-757)
定位：工業透傳老牌，軟體協議擴展性強。
特點：這兩家（眾山與有人網絡）是華南工業物聯網的標配。其特點是支持「邊緣腳本（Script）」，如果你的傳感器 Modbus 協議有些非標準的怪癖，可以在 DTU 後台寫幾行簡單的邏輯進行前置處理。
4. 映翰通 (InHand Networks) —— InDTU332G 系列
定位：中高階工業級，外銷歐美主流品牌（性價比仍優於歐美大廠）。
特點：外殼與硬體防護級別極高（抗浪湧、防靜電），具備強大的「看門狗（Watchdog）」硬體防當機機制。如果你的項目部署在高度無人值守的嚴苛戶外，這款最讓人安心。
5. 邁威通信 (Maiwe) / 碩迪 (Suodi) —— 工業級雙路 RS485 DTU
定位：多總線、多儀器並行採集專用。
特點：提供雙路（2路）獨立的 RS485 接口。因為你有 10 幾種不同的儀器，如果全部串在同一條線上導致通訊衝突，這款 DTU 允許你把 5 個環境傳感器接在 A 線，另 5 個土壤傳感器接在 B 線，在網關內部統一打包發送 MQTT。
5 款 DTU 網關綜合橫向對比表
為了方便你進行採購決策，以下將它們的規格、接口、核心優勢以及預估價格進行對比：
品牌與型號	實體接口	通訊網絡	核心優勢	預估單價 (港幣/人民幣)	方案推薦度
1. 塔石 TAS-LTE-393	RS485 + RS232	4G 全網通	配置極簡單，價格極便宜，文檔齊全。	$150 - $250	
★★★★★

(預算首選)
2. 有方 Neoway N306	RS485	4G 全網通	晶片級訊號優化，野外弱訊號地區極穩。	$220 - $350	★★★★☆
3. 有人 USR-LTE-757	RS485 / 以太網可選	4G + 以太網	內置網絡緩存，斷線時數據不丟失。	$280 - $400	★★★★☆
4. 映翰通 InDTU332	RS485 (高防護)	4G 全網通	通過多項工業認證，抗干擾防雷最強。	$450 - $650	
★★★★★

(戶外穩定首選)
5. 邁威工業網關	雙路 RS485	4G + 以太網	兩路獨立總線，避免多儀器通訊塞車。	$380 - $550	★★★★☆
針對你的方案之採購與選型建議
如果你追求「極致性價比」且環境有防水箱保護：
直接購買 塔石 (Tashit) TAS-LTE-393。它的 Modbus 轉 MQTT JSON 的後台配置非常傻瓜化，完全契合我們第二步寫的 Django 監聽代碼格式，且價格便宜，多買兩台做備份都不心疼。
如果你的儀器佈署在「野外、極端天氣、防雷要求高」的現場：
強烈建議提高一點預算選擇 映翰通 (InHand) InDTU332。工業現場最怕 DTU 因為電壓不穩或雷擊而死機，映翰通的硬體看門狗和電源防護能幫你省下大量的現場維護與跑腿成本。
注意線路布局：
這 5 款不論選哪一款，由於你有接近 20 個儀器讀數，採購時請務必提醒傳感器供應商：「所有儀器的 Modbus 從站地址（Slave ID）必須錯開（例如 01, 02, 03...），且波特率（Baud rate，通常預設 9600）必須保持一致」，這樣 DTU 才能順利進行輪詢。