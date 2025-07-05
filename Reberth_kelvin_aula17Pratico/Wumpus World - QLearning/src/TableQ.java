import java.util.*;

abstract public class TableQ {

    public TableQ(HashMap<MapScenario, ArrayList<MapScenario>> vertices, double learningRate, double compensationRate) {
        this.vertices = new HashMap<>();
        for (MapScenario root : vertices.keySet()) {
            this.vertices.putIfAbsent(root, new ArrayList<>());
            for (MapScenario node : vertices.get(root)) {
                WeighEdge edge = new WeighEdge(0, getRewardScore(node), node);
                this.vertices.get(root).add(edge);
            }
        }
        this.learningRate = learningRate;
        this.compensationRate = compensationRate;
    }

    private HashMap<MapScenario, ArrayList<WeighEdge>> vertices;
    private final double learningRate;
    private final double compensationRate;

    protected abstract int getGoldReward();
    protected abstract int getPitReward();
    protected abstract int getWumpusReward();
    protected abstract int getExitReward();

    public double getLearningRate() {
        return learningRate;
    }

    public double getCompensationRate() {
        return compensationRate;
    }

    public ArrayList<WeighEdge> edgesForNode(MapScenario node) {
        return vertices.get(node);
    }

    public int getRewardScore(MapScenario node) {
        if (node.hasGold()) {
            return getGoldReward();
        }

        if (node.hasWumpus()) {
            return getWumpusReward();
        }

        if (node.hasPit()) {
            return getPitReward();
        }

        if (node.isExit()) {
            return getExitReward();
        }

        return 0;
    }

    public void printWeightsTable() {
        String border = "+------------------+--------------+--------------+--------------+--------------+";
        String headerFormat = "| %-16s | %-12s | %-12s | %-12s | %-12s |%n";
        String rowFormat = "| %-16s | %12s | %12s | %12s | %12s |%n";

        System.out.println("--- Q-Table ---");
        System.out.println(border);
        System.out.printf(headerFormat, "State", "Left", "Right", "Top", "Bottom");
        System.out.println(border);

        List<Map.Entry<MapScenario, ArrayList<WeighEdge>>> sortedEntries = new ArrayList<>(this.vertices.entrySet());
        sortedEntries.sort(Comparator.comparing((Map.Entry<MapScenario, ArrayList<WeighEdge>> e) -> e.getKey().getCoordinate().getX())
                .thenComparing(e -> e.getKey().getCoordinate().getY()));

        for (Map.Entry<MapScenario, ArrayList<WeighEdge>> entry : sortedEntries) {
            MapScenario fromNode = entry.getKey();
            Coordinate fromCoord = fromNode.getCoordinate();

            Map<String, Double> qValuesByDirection = new HashMap<>();

            for (WeighEdge edge : entry.getValue()) {
                Coordinate toCoord = edge.getMapScenario().getCoordinate();

                // Check for horizontal movement
                if (toCoord.getY() == fromCoord.getY()) {
                    if (toCoord.getX() == fromCoord.getX() - 1) {
                        qValuesByDirection.put("Left", edge.getWeight());
                    } else if (toCoord.getX() == fromCoord.getX() + 1) {
                        qValuesByDirection.put("Right", edge.getWeight());
                    }
                }
                // Check for vertical movement
                else if (toCoord.getX() == fromCoord.getX()) {
                    // Assuming Y increases upwards. Top is Y+1, Bottom is Y-1.
                    if (toCoord.getY() == fromCoord.getY() + 1) {
                        qValuesByDirection.put("Top", edge.getWeight());
                    } else if (toCoord.getY() == fromCoord.getY() - 1) {
                        qValuesByDirection.put("Bottom", edge.getWeight());
                    }
                }
            }

            String qLeft = qValuesByDirection.containsKey("Left") ? String.format("%.4f", qValuesByDirection.get("Left")) : "---";
            String qRight = qValuesByDirection.containsKey("Right") ? String.format("%.4f", qValuesByDirection.get("Right")) : "---";
            String qTop = qValuesByDirection.containsKey("Top") ? String.format("%.4f", qValuesByDirection.get("Top")) : "---";
            String qBottom = qValuesByDirection.containsKey("Bottom") ? String.format("%.4f", qValuesByDirection.get("Bottom")) : "---";

            System.out.printf(rowFormat, fromCoord, qLeft, qRight, qTop, qBottom);
        }

        System.out.println(border);
    }

}