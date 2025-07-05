import java.util.ArrayList;
import java.util.HashMap;

public class TakeGoldTableQ extends TableQ {
    public TakeGoldTableQ(HashMap<MapScenario, ArrayList<MapScenario>> vertices, double learningRate, double compensationRate) {
        super(vertices, learningRate, compensationRate);
    }

    @Override
    public int getGoldReward() {
        return 10;
    }

    @Override
    public int getPitReward() {
        return -10;
    }

    @Override
    public int getWumpusReward() {
        return -10;
    }

    @Override
    public int getExitReward() {
        return 0;
    }
}
