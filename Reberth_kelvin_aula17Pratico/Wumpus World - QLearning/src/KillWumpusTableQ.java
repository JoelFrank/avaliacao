import java.util.ArrayList;
import java.util.HashMap;

public class KillWumpusTableQ extends TableQ {

    public KillWumpusTableQ(HashMap<MapScenario, ArrayList<MapScenario>> vertices, double learningRate, double compensationRate) {
        super(vertices, learningRate, compensationRate);
    }

    @Override
    public int getGoldReward() {
        return 0; // No gold reward in this scenario
    }

    @Override
    public int getPitReward() {
        return -10; // Penalty for falling into a pit
    }

    @Override
    public int getWumpusReward() {
        return 10; // Reward for killing the Wumpus
    }

    @Override
    public int getExitReward() {
        return 0; // No exit reward in this scenario
    }
}
