import java.text.SimpleDateFormat;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.security.*;
import java.math.*;
import java.util.concurrent.TimeUnit;

public class FogDeviceLB {

	private int id;
	private String name;
	private int cpuCoreCount;
	private int ram;
	private int storageAmount;
	private int uploadBandwith;
	private int downloadBandwith;
	private int latency;
	private double loadAverage;
	private double maxLoadAverage;
	private int aguardar, dropados;
	private double limiteAceitavelLoadAvg;
	//private List<Long> tempos = new ArrayList<Long>();
	//private List<Double> loadAvg = new ArrayList<Double>();

	public FogDeviceLB(int id, String name, int cpuCoreCount, int ram, int storageAmount, int uploadbandwith,
			int downloadbandwith, int latency) {
		this.id = id;
		this.name = name;
		this.cpuCoreCount = cpuCoreCount;
		this.ram = ram;
		this.storageAmount = storageAmount;
		this.uploadBandwith = uploadbandwith;
		this.downloadBandwith = downloadbandwith;
		this.latency = latency;
		this.aguardar = 0;
		this.dropados = 0;
		this.maxLoadAverage = 100*this.cpuCoreCount; // para o caso de ter mais de 1 core
		this.limiteAceitavelLoadAvg = (this.maxLoadAverage*0.8);
	}

	public void doTask(String data, double latency) throws Exception {

		long StartTime = System.currentTimeMillis();

		// System.out.println("LoadAVG: " + this.loadAverage);
		//LoadBalancer.encaminhados.put(this.id, 1);
		//LoadBalancer.encaminhados.put(this.id, (LoadBalancer.encaminhados.get(this.id) != null ? LoadBalancer.encaminhados.get(this.id) : 0) +1);
		LoadBalancer.encaminhados.computeIfAbsent(this.id, k -> new ArrayList<>()).add(1);

		boolean dropou = false;
		if (this.loadAverage >= this.maxLoadAverage) {
			//System.out.println("Load Alto: " + this.id + " " + this.loadAverage);
			LoadBalancer.droped.computeIfAbsent(this.id, k -> new ArrayList<>()).add(1);
			dropou = true;
			while (this.loadAverage >= this.maxLoadAverage) { // aguarda até que load seja < 100
				TimeUnit.MILLISECONDS.sleep(10);
			}
		}

		if (!dropou) { // se pacote não foi dropado, processa-o
			this.loadAverage += 5;

			if ((this.loadAverage >= this.limiteAceitavelLoadAvg)) { // se a fog está ficando sobrecarregada, penaliza o tempo de processamento
											// do dado
//				System.out.println("Fog está sobrecarregada");			
				this.aguardar += 10;
				TimeUnit.MILLISECONDS.sleep(this.aguardar);
			}

			TimeUnit.MILLISECONDS.sleep((long) latency);
			MessageDigest m = MessageDigest.getInstance("MD5");
			m.update(data.getBytes(), 0, data.length());

			long StopTime = System.currentTimeMillis();
			Long elapsedTime = StopTime - StartTime;
			// System.out.println("Tempo decorrido: " + (elapsedTime));

			try {
				synchronized (this) {
					//System.out.println("id: " + this.id + " loadAvg: " + this.loadAverage + " tempo decorrido: " + elapsedTime);
					LoadBalancer.tempos.computeIfAbsent(this.id, k -> new ArrayList<>()).add(elapsedTime);
					LoadBalancer.loads.computeIfAbsent(this.id, k -> new ArrayList<>()).add(this.loadAverage);
				}
			} catch (Exception e) {
				e.printStackTrace();
			}

			if (this.loadAverage != 0) {
				this.loadAverage -= 5;
			}			

		}

	}

	public int getId() {
		return this.id;
	}

	public int getDropados() {
		return this.dropados;
	}	

	public int getCpuCoreCount() {
		return this.cpuCoreCount;
	}

	public int getRam() {
		return this.ram;
	}

	public int getStorageAmount() {
		return this.storageAmount;
	}

	public int getUploadBandwidth() {
		return this.uploadBandwith;
	}

	public int getDownloadBandwidth() {
		return this.downloadBandwith;
	}

	public int getLatency() {
		return this.latency;
	}

	public String getName() {
		return this.name;
	}

	public double getLoadAverage() {
		return this.loadAverage;
	}	

}
