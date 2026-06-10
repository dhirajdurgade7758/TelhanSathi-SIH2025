IoT Module Integration: The Sentinel

The Necessity of IoT in Telhan Sathi

While satellite imagery (such as Sentinel-2) provides excellent regional-scale data, a pure software approach has critical limitations in agriculture:

1.The Monsoon Blind Spot: Heavy cloud cover during the Indian monsoon season renders satellite optical imagery highly inaccurate when farmers need it the most.
2.Generic API Inaccuracies: Standard weather APIs provide data at a district or block level, completely missing the highly variable, farm-level micro-climates.

The Solution: We integrated a custom-built, low-cost IoT node dubbed "The Sentinel." This device acts as the ground truth anchor for our ecosystem. By capturing hyper-local micro-climate, light, and soil data directly from the field, the IoT node calibrates our Machine Learning models, filling in the data gaps left by satellites and significantly boosting our predictive accuracy.

Hardware Architecture & Components

The Sentinel is designed for autonomous, on-field deployment. It comprises the following core hardware components:

Microcontroller Unit (MCU): The core processor responsible for reading sensor data and transmitting it securely to our centralized backend.
Soil Moisture Sensor: Measures the volumetric water content in the soil, providing real-time data on hydration levels to aid in precision irrigation.

DS18B20 Sensor: A waterproof temperature sensor submerged in the soil to track precise root-level thermal conditions.

DHT22 Sensor: Monitors ambient temperature and high-precision humidity directly above the crop canopy.

LDR (Light Dependent Resistor) Sensor: Measures ambient light intensity to track the duration and strength of sunlight exposure (photoperiod) over the field.

16x2 LCD Display: Added for immediate, on-site data visibility. This allows farmers to view real-time soil, weather, and light parameters directly in the field without needing to open a mobile application.

Battery & Charging Module: To ensure uninterrupted field operation, the node is equipped with a rechargeable battery paired with a dedicated charging module (TP4056). This enables the device to run autonomously and supports easy integration with small solar panels for off-grid power.

Software & Backend Integration

The integration between the hardware and the Telhan Sathi software ecosystem operates in a seamless, real-time loop:

1. Data Acquisition: The MCU reads signals from the Soil Moisture, DS18B20, DHT22, and LDR sensors at predefined intervals.
2. Local Display: The acquired data is instantly pushed to the 16x2 LCD for on-site monitoring.
3. Cloud Transmission: The formatted data payload is transmitted to our backend server via wireless protocols (Wi-Fi/GSM).
4. ML Calibration: The backend routes this hyper-local data into our Machine Learning pipeline. The ML engine cross-references this ground truth data with satellite inputs, correcting discrepancies and generating highly accurate crop yield and disease predictions.

Key Benefits of the IoT Ecosystem

Consistent Data Uptime: Bypasses satellite blind spots during cloudy or extreme weather conditions.
Comprehensive Metrics: Tracks everything from soil hydration to sunlight intensity, creating a complete micro-climate profile.
Farmer-Centric Accessibility: The LCD screen ensures that users without immediate smartphone access can still monitor their farm's health.
Autonomous Operation: The integrated battery and charging module ensure longevity, continuous power, and minimal maintenance for the end user.