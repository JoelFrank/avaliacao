public class WeighEdge {
    public WeighEdge(int weight, int reward, MapScenario mapScenario) {
        this.weight = weight;
        this.reward = reward;
        this.mapScenario = mapScenario;
    }

    private double weight;
    private int reward;
    private MapScenario mapScenario;

    public MapScenario getMapScenario() {
        return mapScenario;
    }

    public void setWeight(double weight) {
        this.weight = weight;
    }

    public void setReward(int reward) {
        this.reward = reward;
    }

    public double getWeight() {
        return weight;
    }

    public int getReward() {
        return reward;
    }
}
