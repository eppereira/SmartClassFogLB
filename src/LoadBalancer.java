import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

public class LoadBalancer {

    private List<FogDeviceLB> fogDevices;
    private int id;

    public static Map<Integer, List<Integer>> encaminhados = new HashMap<>();
    public static Map<Integer, List<Integer>> droped = new HashMap<>();

    public static Map<Integer, List<Long>> tempos = new HashMap<>();
    public static Map<Integer, List<Double>> loads = new HashMap<>();

    public LoadBalancer(List<FogDeviceLB> fogs, int id) {
        this.fogDevices = new ArrayList<FogDeviceLB>();
        this.fogDevices = fogs;
        this.id = id;
    }

    public void allocateTask(int idSensor, int priority, double latency, String data) {

        try {

            if (this.fogDevices.size() == 1) { // se tem só 1 nó, naõ precisa ordenar
                fogDevices.get(0).doTask(data, latency);
            } else {
                getBestFogDevice(priority).doTask(data, latency);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public FogDeviceLB getBestFogDevice(int priority) throws InterruptedException {
        // avalia qual nó da fog é mais apropriado

        synchronized (this) {

            if (priority == 1) {
                // alta prioridade, pega o melhor nó, com menor loadavg
                //System.out.println("alta prio");
                fogDevices.sort((o1, o2) -> {

                    // menor load average
                    if (o1.getLoadAverage() != o2.getLoadAverage()) {
                        return (int) (o1.getLoadAverage() - o2.getLoadAverage());
                    }

                    // maior número de cpus
                    if (o1.getCpuCoreCount() != o2.getCpuCoreCount()) {
                        return o2.getCpuCoreCount() - o1.getCpuCoreCount();
                    }

                    // CPU empatada. Agora ordena por memoria (mais primeiro)
                    if (o1.getRam() != o2.getRam()) {
                        return o2.getRam() - o1.getRam();
                    }

                    if (o1.getStorageAmount() != o2.getStorageAmount()) {
                        return o2.getStorageAmount() - o1.getStorageAmount();
                    }

                    if (o1.getUploadBandwidth() != o2.getUploadBandwidth()) {
                        return o2.getUploadBandwidth() - o1.getUploadBandwidth();
                    }

                    if (o1.getDownloadBandwidth() != o2.getDownloadBandwidth()) {
                        return o2.getDownloadBandwidth() - o1.getDownloadBandwidth();
                    }
                    // menor latência
                    if (o1.getLatency() != o2.getLatency()) {
                        return o1.getLatency() - o2.getLatency();
                    }

                    return 0;

                });
                //System.out.println("Fog eleita: " + fogDevices.get(0).getName());
                if (fogDevices.get(0).getLoadAverage() >= (fogDevices.get(0).getCpuCoreCount() * 100) * 0.8) { //se o melhor nó está sobrecarregado (acima de 80%), retorna o segundo da lista
                    //System.out.println("Fog eleita: " + fogDevices.get(0).getName() + " está sobrecarregada: " + fogDevices.get(0).getLoadAverage());
                    //return fogDevices.get(1);
                }
                return fogDevices.get(0);

            } else {
                // baixa prioridade, pega o nó com menor loadavg
                fogDevices.sort((o1, o2) -> {
                    // menor load average
                    if (o1.getLoadAverage() != o2.getLoadAverage()) {
                        return (int) (o1.getLoadAverage() - o2.getLoadAverage());
                    }
                    return 0;
                });
                //System.out.println("Fog eleita: " + fogDevices.get(0).getName());
                return fogDevices.get(0);
            }
        }

    }

    public int getId() {
        return this.id;
    }

}
