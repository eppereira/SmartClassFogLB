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

public class FogDevice {

	private int id;
	private String name;
	private int cpuCoreCount;
	private int ram;
	private int storageAmount;
	private int uploadBandwith;
	private int downloadBandwith;
	private int latency;
	private double loadAverage;
	private int aguardar, dropados;
	private List<Long> tempos = new ArrayList<Long>();
	private List<Double> loadAvg = new ArrayList<Double>();

	public FogDevice(int id, String name, int cpuCoreCount, int ram, int storageAmount, int uploadbandwith,
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
	}

	public void doTask(String data, double latency) throws Exception {

		long StartTime = System.currentTimeMillis();
		// System.out.println("LoadAVG: " + this.loadAverage);

		boolean dropou = false;
		if (this.loadAverage >= 100) {
			dropados++;
			dropou = true;
			while (this.loadAverage >= 100) { // aguarda até que load seja < 100
				TimeUnit.MILLISECONDS.sleep(10);
			}
		}

		if (!dropou) { // se pacote não foi dropado, processa-o
			this.loadAverage += 5;
			if ((this.loadAverage >= 80)) { // se a fog está ficando sobrecarregada, penaliza o tempo de processamento
											// do dado
//				System.out.println("Fog está sobrecarregada");			
				this.aguardar += 10;
				TimeUnit.MILLISECONDS.sleep(this.aguardar);
			}

			TimeUnit.MILLISECONDS.sleep((long) latency);
			MessageDigest m = MessageDigest.getInstance("MD5");
			m.update(data.getBytes(), 0, data.length());

			long StopTime = System.currentTimeMillis();
			long elapsedTime = StopTime - StartTime;
			// System.out.println("Tempo decorrido: " + (elapsedTime));

			try {
				this.tempos.add(elapsedTime);
				this.loadAvg.add(this.loadAverage);
			} catch (Exception e) {
				e.printStackTrace();
			}

			this.loadAverage -= 5;

		}
	}

	public int getId() {
		return this.id;
	}

	public int getDropados() {
		return this.dropados;
	}

	public List<Long> getTempos() {
		return this.tempos;
	}

	public List<Double> getLoads() {
		return this.loadAvg;
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
