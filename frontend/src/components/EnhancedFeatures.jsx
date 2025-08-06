import React, { useState, useEffect } from 'react';
import { Upload, Camera, Zap, Brain, TrendingUp, Home, Wifi, DollarSign } from 'lucide-react';

const EnhancedFeatures = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageAnalysis, setImageAnalysis] = useState(null);
  const [iotDevices, setIotDevices] = useState([]);
  const [energyReport, setEnergyReport] = useState(null);
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSystemStatus();
    fetchIoTDevices();
    fetchEnergyReport();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/system/status');
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  const fetchIoTDevices = async () => {
    try {
      const response = await fetch('/api/enhanced/iot/devices');
      if (response.ok) {
        const data = await response.json();
        setIotDevices(data.devices || []);
      }
    } catch (error) {
      console.error('Error fetching IoT devices:', error);
    }
  };

  const fetchEnergyReport = async () => {
    try {
      const response = await fetch('/api/enhanced/iot/energy-report?days=7');
      if (response.ok) {
        const data = await response.json();
        setEnergyReport(data);
      }
    } catch (error) {
      console.error('Error fetching energy report:', error);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      const imageData = e.target.result;
      setSelectedImage(imageData);
      
      try {
        const response = await fetch('/api/enhanced/image-analysis', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image: imageData }),
        });
        
        if (response.ok) {
          const data = await response.json();
          setImageAnalysis(data.analysis);
        } else {
          console.error('Image analysis failed');
        }
      } catch (error) {
        console.error('Error analyzing image:', error);
      } finally {
        setLoading(false);
      }
    };
    
    reader.readAsDataURL(file);
  };

  const controlDevice = async (deviceId, action, parameters = {}) => {
    try {
      const response = await fetch('/api/enhanced/iot/control', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_id: deviceId,
          action: action,
          parameters: parameters,
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Device control result:', result);
        fetchIoTDevices(); // Refresh device list
      }
    } catch (error) {
      console.error('Error controlling device:', error);
    }
  };

  const checkPrices = async (components) => {
    setLoading(true);
    try {
      const response = await fetch('/api/enhanced/price-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ components }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setPriceData(data.price_data);
      }
    } catch (error) {
      console.error('Error checking prices:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!systemStatus) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            TechCraft Genius AI - Enhanced Platform
          </h1>
          <p className="text-xl text-gray-600">
            Full AI capabilities with multi-provider integration, computer vision, and IoT control
          </p>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <Brain className="mr-2 text-blue-600" />
            System Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                systemStatus.enhanced_features ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {systemStatus.enhanced_features ? '✓ Enhanced Features Active' : '✗ Basic Mode Only'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {systemStatus.ai_providers?.length || 0}
              </div>
              <div className="text-sm text-gray-600">AI Providers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {systemStatus.iot_online || 0}/{systemStatus.iot_devices || 0}
              </div>
              <div className="text-sm text-gray-600">Devices Online</div>
            </div>
          </div>
        </div>

        {/* Enhanced Features Grid */}
        {systemStatus.enhanced_features && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Image Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <Camera className="mr-2 text-purple-600" />
                Computer Vision Analysis
              </h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Room Photo for Automation Analysis
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>

              {selectedImage && (
                <div className="mb-4">
                  <img
                    src={selectedImage}
                    alt="Uploaded room"
                    className="w-full h-48 object-cover rounded-lg"
                  />
                </div>
              )}

              {loading && (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-600">Analyzing image...</p>
                </div>
              )}

              {imageAnalysis && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Analysis Results:</h4>
                  <div className="space-y-2 text-sm">
                    <p><strong>Room Type:</strong> {imageAnalysis.room_type} ({(imageAnalysis.confidence * 100).toFixed(1)}% confidence)</p>
                    <p><strong>Estimated Size:</strong> {imageAnalysis.dimensions[0]}m × {imageAnalysis.dimensions[1]}m</p>
                    <p><strong>Lighting:</strong> {imageAnalysis.lighting}</p>
                    <p><strong>Detected Devices:</strong> {imageAnalysis.devices.length}</p>
                  </div>
                  
                  {imageAnalysis.suggestions.length > 0 && (
                    <div className="mt-4">
                      <h5 className="font-semibold mb-2">Automation Suggestions:</h5>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {imageAnalysis.suggestions.slice(0, 5).map((suggestion, index) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* IoT Device Control */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <Home className="mr-2 text-green-600" />
                Smart Home Control
              </h3>
              
              <div className="space-y-4">
                {iotDevices.slice(0, 5).map((device) => (
                  <div key={device.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold">{device.name}</h4>
                        <p className="text-sm text-gray-600">{device.brand} {device.model}</p>
                        <p className="text-sm text-gray-500">{device.room}</p>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        device.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {device.status}
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      {device.device_type === 'light' && (
                        <>
                          <button
                            onClick={() => controlDevice(device.id, 'turn_on')}
                            className="px-3 py-1 bg-yellow-500 text-white rounded text-sm hover:bg-yellow-600"
                          >
                            Turn On
                          </button>
                          <button
                            onClick={() => controlDevice(device.id, 'turn_off')}
                            className="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
                          >
                            Turn Off
                          </button>
                        </>
                      )}
                      
                      {device.device_type === 'plug' && (
                        <>
                          <button
                            onClick={() => controlDevice(device.id, 'turn_on')}
                            className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                          >
                            Enable
                          </button>
                          <button
                            onClick={() => controlDevice(device.id, 'turn_off')}
                            className="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
                          >
                            Disable
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Energy Monitoring */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <Zap className="mr-2 text-yellow-600" />
                Energy Monitoring
              </h3>
              
              {energyReport && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        £{energyReport.total_estimated_daily_cost}
                      </div>
                      <div className="text-sm text-gray-600">Daily Cost</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        £{energyReport.total_estimated_monthly_cost}
                      </div>
                      <div className="text-sm text-gray-600">Monthly Est.</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-semibold">Device Breakdown:</h4>
                    {energyReport.device_reports.slice(0, 5).map((report, index) => (
                      <div key={index} className="flex justify-between items-center py-2 border-b">
                        <span className="text-sm">{report.device_name}</span>
                        <div className="text-right">
                          <div className="text-sm font-medium">£{report.average_daily_cost}/day</div>
                          <div className="text-xs text-gray-500">{report.average_power}W</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Price Monitoring */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <DollarSign className="mr-2 text-green-600" />
                Real-time Price Monitoring
              </h3>
              
              <div className="mb-4">
                <button
                  onClick={() => checkPrices(['raspberry pi', 'arduino', 'smart bulb'])}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Checking Prices...' : 'Check Component Prices'}
                </button>
              </div>

              {priceData && (
                <div className="space-y-4">
                  {Object.entries(priceData).map(([component, prices]) => (
                    <div key={component} className="border rounded-lg p-3">
                      <h4 className="font-semibold capitalize mb-2">{component}</h4>
                      <div className="space-y-1">
                        {prices.slice(0, 3).map((price, index) => (
                          <div key={index} className="flex justify-between items-center text-sm">
                            <span>{price.supplier}</span>
                            <div className="text-right">
                              <div className="font-medium">£{price.price}</div>
                              <div className="text-xs text-gray-500">{price.availability}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Basic Mode Message */}
        {!systemStatus.enhanced_features && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">
              Enhanced Features Not Available
            </h3>
            <p className="text-yellow-700">
              The platform is running in basic mode. Enhanced AI capabilities, computer vision, 
              IoT control, and real-time data collection are currently disabled.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedFeatures;

