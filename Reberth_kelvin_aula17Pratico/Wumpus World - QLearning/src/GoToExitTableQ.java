import java.util.ArrayList;
import java.util.HashMap;

public class GoToExitTableQ extends TableQ{
    public GoToExitTableQ(HashMap<MapScenario, ArrayList<MapScenario>> vertices, double learningRate, double compensationRate) {
        super(vertices, learningRate, compensationRate);
    }

    @Override
    protected int getGoldReward() {
        return 0;
    }

    @Override
    protected int getPitReward() {
        return -10;
    }

    @Override
    protected int getWumpusReward() {
        return 0;
    }

    @Override
    protected int getExitReward() {
        return 10;
    }
}
