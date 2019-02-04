import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

public class TestaLB {


	// soma dos encaminhados naõ bate com o número de sensores;

	private static final int SENSORES = 10000;
	private static final int FOGS = 10;
	private static final int LATENCIASENSORES = 10;
	private static final int PRIORIDADE = 1;
	private static final int REQUISISOES = 1;
	private static final int SLEEP = 0;

	public static void main(String[] args) throws Exception {
		// TODO Auto-generated method stub

		System.out.println("Começando o teste com " + SENSORES + " sensores e " + FOGS + " Nós de Fog.");
		List<FogDeviceLB> fogs = new ArrayList<>();

		for (int i = 1; i <= FOGS; i++) {
			fogs.add(new FogDeviceLB(i, "", 1, 1, 10, 10, 50, 15));
		}

		LoadBalancer lb = new LoadBalancer(fogs, 1);

		List<SensorLB> sensores = new ArrayList<SensorLB>();
		for (int i = 0; i < SENSORES; i++) {
			// int id, String name, int gatewayId, double latency, int priority
			Random prio = new Random();
			int prioridade = prio.nextInt(1);
			sensores.add(new SensorLB(i, "", lb.getId(), LATENCIASENSORES, PRIORIDADE));
			// sensores.add(new SensorLB(i, "", lb.getId(), LATENCIASENSORES, 1);
		}
		List<Thread> threads = new ArrayList<>();

		for (SensorLB s : sensores) {
			Thread t = new Thread() {
				@Override
				public void run() {
					// System.out.println("Dentro da thread...");
					Random string = new Random();
					byte[] array = new byte[10];
					string.nextBytes(array);
					for (int j = 0; j < REQUISISOES; j++) {
						try {
							// LoadBalancer Gateway, int id, int priority, double latency, String data
							s.sendData(lb, s.getId(), s.getPriority(), s.getLatency(), string.toString());
							Thread.sleep(SLEEP);
						} catch (Exception e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
					}
				}
			};

			t.start();
			threads.add(t);
		}

		for (Thread t : threads)
			t.join();

		List<Integer> mediaPctDropados = new ArrayList<>();
		List<Long> mediaPctTempos = new ArrayList<>();
		List<Long> mediaPctTemposMax = new ArrayList<>();
		List<Long> mediaPctTemposMin = new ArrayList<>();
		List<Double> mediaPctLoadAvg= new ArrayList<>();

		for (int i = 1; i <= FOGS; i++) {
			//System.out.println("\n\nEstatísticas para Fog" + i);
			int aux = 0;

			// encaminhados
			
			List<Integer> enc = new ArrayList<>();
			for (Integer e : LoadBalancer.encaminhados.keySet()) {
				if (e == i) {
					enc = LoadBalancer.encaminhados.get(e);
				}
			}
			//System.out.println("Requisições Encaminhadas: " + enc.size());
			// aux = 0;
			// droped
			List<Integer> drop = new ArrayList<>();
			for (Integer d : LoadBalancer.droped.keySet()) {
				if (d == i) {
					drop = LoadBalancer.droped.get(d);
				}
			}

			//System.out.println("Dropados: " + drop.size());

			// tempo medio

			double media = 0;
			List<Long> tempos = new ArrayList<>();
			for (Integer t : LoadBalancer.tempos.keySet()) {
				if (t == i) {
					tempos = LoadBalancer.tempos.get(t);
				}
			}

			int temp = 0;
			for (Long t : tempos) {
				temp += t;

			}
			if (tempos.size() != 0) {
				media = temp / tempos.size();
				mediaPctTempos.add((long) media);
			}
			//System.out.println("Tempo Médio: " + (media > 0 ? media : 0));
			
			//aux = 0;
			//media = 0;
			// load avg medio
			List<Double> loads = new ArrayList<>();
			for (Integer l : LoadBalancer.loads.keySet()) {
				if (l == i) {
					loads = LoadBalancer.loads.get(l);
				}
			}
			int medio = 0;
			for (Double d : loads) {
				medio += d;
			}
			if (loads.size() != 0) {
				media = medio / loads.size();
			}

			Long temMax = (tempos.size() > 0 ? Collections.max(tempos) : Long.valueOf(0));
			mediaPctTemposMax.add(temMax);
			Long temMin = (tempos.size() > 0 ? Collections.min(tempos): Long.valueOf(0));
			mediaPctTemposMin.add(temMin);
			mediaPctLoadAvg.add(media > 0 ? media : 0);

			/*System.out.println("Load Máximo: " + (loads.size() > 0 ? Collections.max(loads) : 0)
					+ "\nLoad Mínimo: " + (loads.size() > 0 ? Collections.min(loads): 0)
					+ "\nMedia de load: " + (media > 0 ? media : 0));
			*/
		}

		Double mediaDropedFinal = 0.0;
		for (Integer x : mediaPctDropados){
			mediaDropedFinal += x;
		}
		mediaDropedFinal = mediaDropedFinal/mediaPctDropados.size();
		Double mediaTempoFinal = 0.0;
		for (Long j : mediaPctTempos){
			mediaTempoFinal += j;
		}
		mediaTempoFinal = mediaTempoFinal/mediaPctTempos.size();

		Double mediaTempoMaxFinal = 0.0;
		for (Long w : mediaPctTemposMax){
			mediaTempoMaxFinal += w;
		}
		mediaTempoMaxFinal = mediaTempoMaxFinal/mediaPctTemposMax.size();

		Double mediaTempoMinFinal = 0.0;
		for (Long y : mediaPctTemposMin){
			mediaTempoMinFinal += y;
		}
		mediaTempoMinFinal = mediaTempoFinal/mediaPctTemposMin.size();

		Double mediaLoadFinal = 0.0;
		for (Double t : mediaPctLoadAvg){
			mediaLoadFinal += t;
		}
		mediaLoadFinal = mediaLoadFinal/mediaPctLoadAvg.size();
		System.out.println("=============================================="
							+ "\nEstatísticas do cluster no geral (dados agrupados das médias dos nós da fog):"
							+"\n\nMédia de dropados do cluster: " + (mediaDropedFinal > 0 ? mediaDropedFinal : 0)
							+ "\nMédia de tempo máximo do cluster: " + mediaTempoMaxFinal + " com " + mediaPctTemposMax.size() + " leituras"
							+ "\nMédia de tempo mínimo do cluster: " + mediaTempoMinFinal + " com " + mediaPctTemposMin.size() + " leituras"
							+ "\nMédia de tempo Médio do cluster: " + mediaTempoFinal
							+ "\nMédia de Load do cluster: " + mediaLoadFinal
							+ "\n==============================================");
		System.out.println("\n\nSimulação terminada.");
	}

	public strictfp Double getDesvioPadrao(List<Double> valor) {
		//Double media = getMedia(valor); TODO IMPLEMENTAR UMA FORMA DE OBTER AS MÉDIAS PARA O DESVIO PADRÃO
		int tam = valor.size();
		Double desvPadrao = 0D;
		for (Double vlr : valor) {
			// Double aux = vlr - media; TODO
			// desvPadrao += aux * aux; TODO
		}
		return Math.sqrt(desvPadrao / (tam - 1));
	}

}
