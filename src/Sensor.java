public class Sensor {
	
	private int id;
	private String name;
	private int gatewayId;
	private double latency;
	
	public Sensor(int id, String name, int gatewayId, double latency) {
		this.id = id;
		this.name = name;
		this.gatewayId = gatewayId;		
		this.latency = latency;
	}
	
	public void sendData(FogDevice Gateway, String data) throws Exception {		
		Gateway.doTask(data, this.latency);
	}
	
	public double getLatency() {
		return this.latency;
	}
	

}
