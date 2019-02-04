import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class Testa {

	private static final int SENSORES = 1000;
	private static final int LATENCIASENSORES = 10;

	public static void main(String[] args) throws Exception {
		// TODO Auto-generated method stub

		FogDevice f1 = new FogDevice(1, "f1", 1, 1, 10, 10, 50, 15);
		List<Sensor> sensores = new ArrayList<Sensor>();
		for (int i = 0; i < SENSORES; i++) {
			sensores.add(new Sensor(i, "", f1.getId(), LATENCIASENSORES));
		}
		List<Thread> threads = new ArrayList<>();

		for (Sensor s : sensores) {
			Thread t = new Thread() {
				@Override
				public void run() {
					// System.out.println("Dentro da thread...");
					Random string = new Random();
					byte[] array = new byte[10];
					string.nextBytes(array);
					try {
						s.sendData(f1, string.toString());
					} catch (Exception e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}
			};

			t.start();
			threads.add(t);
		}

		// TimeUnit.SECONDS.sleep(20);

		for (Thread t : threads)
			t.join();

		List<Long> t = f1.getTempos();
		double somaTempos = 0;
		for (Long aux : t) {
			if (aux == null)
				continue; // gambiarra
			somaTempos += aux;
		}

		double mediaTempo = somaTempos / (SENSORES - f1.getDropados());
		Long max = Collections.max(t);
		Long min = Collections.min(t);

		List<Double> mediaLoad = new ArrayList<Double>();
		mediaLoad = f1.getLoads();
		double auxLoad = 0;
		for (Double load : mediaLoad) {
			if(load == null) continue;
			auxLoad += load;
		}

		double mediaLoadFinal = auxLoad / (mediaLoad.size());

		System.out.println("Sensores: " + SENSORES + "\nPacotes Dropados: " + f1.getDropados() + "\nLatência Sensores: "
				+ LATENCIASENSORES + "ms" + "\nTempo Máximo: " + max + "ms" + "\nTempo Mínimo: " + min + "ms"
				+ "\nTempo Médio: " + mediaTempo + "ms" + "\nMedia LoadAvg: " + mediaLoadFinal);
		// Random r = new Random();
		// System.out.println("Random: " + r.nextInt(25));
		// System.gc();

		/*
		 * FogDevice f1 = new FogDevice(1, "f1", 1, 1, 10, 10, 50, 15); List<Sensor>
		 * sensores = new ArrayList<Sensor>(); for (int i = 0; i < SENSORES; i++) {
		 * sensores.add(new Sensor(i, "", f1.getId(), LATENCIASENSORES)); } for (Sensor
		 * s : sensores) { new Thread() {
		 * 
		 * @Override public void run() { //System.out.println("Dentro da thread...");
		 * Random string = new Random(); byte[] array = new byte[10];
		 * string.nextBytes(array); try { s.sendData(f1, string.toString()); } catch
		 * (Exception e) { // TODO Auto-generated catch block e.printStackTrace(); } }
		 * }.start(); } TimeUnit.SECONDS.sleep(20);
		 * 
		 * List<Long> t = new ArrayList<Long>(); t = f1.getTempos(); double somaTempos =
		 * 0; for (Long aux: t) { somaTempos += aux; }
		 * 
		 * double mediaTempo = somaTempos/(SENSORES-f1.getDropados()); Long max =
		 * Collections.max(t); Long min = Collections.min(t);
		 * 
		 * List<Double> mediaLoad = new ArrayList<Double>(); mediaLoad = f1.getLoads();
		 * double auxLoad = 0; for (Double load: mediaLoad) { auxLoad += load; }
		 * 
		 * double mediaLoadFinal = auxLoad/(mediaLoad.size());
		 * 
		 * System.out.println("Sensores: " + SENSORES + "\nPacotes Dropados: " +
		 * f1.getDropados() + "\nLatência Sensores: " + LATENCIASENSORES + "ms" +
		 * "\nTempo Máximo: " + max + "ms" + "\nTempo Mínimo: " + min + "ms" +
		 * "\nTempo Médio: " + mediaTempo + "ms" + "\nMedia LoadAvg: " +
		 * mediaLoadFinal); //Random r = new Random(); //System.out.println("Random: " +
		 * r.nextInt(25)); System.gc();
		 */
	}
}
