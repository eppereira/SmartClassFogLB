public class SensorLB {
	
	private int id;
	private String name;
	private int gatewayId;
	private double latency;
	private int priority;
	
	public SensorLB(int id, String name, int gatewayId, double latency, int priority) {
		this.id = id;
		this.name = name;
		this.gatewayId = gatewayId;		
		this.latency = latency;
		this.priority = priority;
	}
	
	// int idSensor, int priority, double latency, String data
	public void sendData(LoadBalancer Gateway, int id, int priority, double latency, String data) throws Exception {		
		Gateway.allocateTask(id, priority, latency, data);
	}
	
	public double getLatency() {
		return this.latency;
	}
	
	public int getPriority() {
		return this.priority;
	}
	public int getId() {
		return this.id;
	}
	

}
