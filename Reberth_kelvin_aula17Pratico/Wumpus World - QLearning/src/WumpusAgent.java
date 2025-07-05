import java.util.ArrayList;
import java.util.Comparator;
import java.util.Random;

public class WumpusAgent {
    public WumpusAgent() {
        wumpusWorld = new WumpusWorld();
        graph = wumpusWorld.getGraph();
        takeGoldTableQ = new TakeGoldTableQ(graph.getVertices(), 0.1, 0.9);
        killWumpusTableQ = new KillWumpusTableQ(graph.getVertices(), 0.1, 0.9);
        goToExitTableQ = new GoToExitTableQ(graph.getVertices(), 0.1, 0.9);
        this.random = new Random();
    }

    private final WumpusWorld wumpusWorld;
    private final MapGraph graph;
    private final TakeGoldTableQ takeGoldTableQ;
    private final KillWumpusTableQ killWumpusTableQ;
    private final GoToExitTableQ goToExitTableQ;
    private final Random random;

    private boolean wumpusDead = false;
    private boolean goldHasBeenTaken = false;
    private int finalScore = 100;
    private int scoreWhenTakingGold = 100;
    private int scoreWhenKilledWumpus;
    private int shootsRemaining = 1;
    private State state = State.TAKE_GOLD;

    private final Coordinate rootCoordinate = new Coordinate(0, 0);
    private Coordinate playerPosition = rootCoordinate;
    private Coordinate playerPositionWhenTakeGold;
    private Coordinate playerPositionWhenWumpusIsDead;

    public void run() {
        while (state != State.OUT_OF_THE_CAVE) {
            MapScenario playerNode = graph.getNodeByCord(playerPosition);
            TableQ currentTable = getCurrentTable();
            ArrayList<WeighEdge> edges = currentTable.edgesForNode(playerNode);

            if (edges == null || edges.isEmpty()) {
                resetAgentToLastCheckpoint();
                continue;
            }

            boolean isExploring = random.nextDouble() < 0.1;
            WeighEdge chosenEdge = selectAction(edges, isExploring);

            try {
                boolean success = executeAction(chosenEdge, isExploring);
                updateQValue(chosenEdge, currentTable, success);

                if (success) {
                    handleSuccess();
                } else {
                    finalScore--;
                }
            } catch (Exception e) {
                updateQValue(chosenEdge, currentTable, true);
                handleFailure(e);
            }
        }
        printSummary();
    }

    private TableQ getCurrentTable() {
        switch (state) {
            case TAKE_GOLD:
                return takeGoldTableQ;
            case TRYING_KILL_WUMPUS:
                return killWumpusTableQ;
            case GO_TO_EXIT:
                return goToExitTableQ;
            default:
                return null;
        }
    }

    private WeighEdge selectAction(ArrayList<WeighEdge> edges, boolean isExploring) {
        if (isExploring) {
            return edges.get(random.nextInt(edges.size()));
        }
        return edges.stream().max(Comparator.comparingDouble(WeighEdge::getWeight)).get();
    }

    private boolean executeAction(WeighEdge edge, boolean isExploring) throws Exception {
        Direction direction = findDirectionTo(edge.getMapScenario().getCoordinate());
        switch (state) {
            case TAKE_GOLD:
                movePlayer(direction);
                if (wumpusWorld.hasGold(playerPosition)) {
                    wumpusWorld.takeGold(playerPosition);
                    return true;
                }
                return false;
            case TRYING_KILL_WUMPUS:
                if (!isExploring && edge.getWeight() > 0 && shootsRemaining > 0) {
                    wumpusWorld.shootWumpus(direction);
                    return true;
                }
                movePlayer(direction);
                return false;
            case GO_TO_EXIT:
                movePlayer(direction);
                return wumpusWorld.isExit(playerPosition);
        }
        return false;
    }

    private void updateQValue(WeighEdge edge, TableQ table, boolean isTerminal) {
        double weight = edge.getWeight();
        double reward = edge.getReward();
        double learningRate = table.getLearningRate();
        double compensationRate = table.getCompensationRate();
        double maxNextQ = 0.0;

        if (!isTerminal) {
            maxNextQ = table.edgesForNode(edge.getMapScenario()).stream().mapToDouble(WeighEdge::getWeight).max().orElse(0.0);
        }

        edge.setWeight(weight + learningRate * (reward + compensationRate * maxNextQ - weight));
    }

    private void handleSuccess() {
        switch (state) {
            case TAKE_GOLD:
                System.out.println("[TAKE_GOLD] Agent found the gold at: " + playerPosition);
                goldHasBeenTaken = true;
                finalScore += 50;
                scoreWhenTakingGold = finalScore;
                playerPositionWhenTakeGold = playerPosition;
                state = State.TRYING_KILL_WUMPUS;
                System.out.println("--> State changed to TRYING_KILL_WUMPUS");
                break;
            case TRYING_KILL_WUMPUS:
                System.out.println("[KILL_WUMPUS] Agent shot and killed the Wumpus.");
                wumpusDead = true;
                shootsRemaining--;
                finalScore += 50;
                scoreWhenKilledWumpus = finalScore;
                playerPositionWhenWumpusIsDead = playerPosition;
                state = State.GO_TO_EXIT;
                System.out.println("--> State changed to GO_TO_EXIT");
                break;
            case GO_TO_EXIT:
                System.out.println("[GO_TO_EXIT] Agent has reached the exit at: " + playerPosition);
                finalScore += 50;
                state = State.OUT_OF_THE_CAVE;
                System.out.println("--> State changed to OUT_OF_THE_CAVE");
                break;
        }
    }

    private void handleFailure(Exception e) {
        if ("YOU MISSED THE SHOOT!".equals(e.getMessage())) {
            System.out.println("[KILL_WUMPUS] Agent missed the shot. Arrow lost.");
            shootsRemaining--;
        }
        resetAgentToLastCheckpoint();
    }

    private void resetAgentToLastCheckpoint() {
        switch (state) {
            case TAKE_GOLD:
                playerPosition = rootCoordinate;
                finalScore = 100;
                break;
            case TRYING_KILL_WUMPUS:
                playerPosition = playerPositionWhenTakeGold;
                finalScore = scoreWhenTakingGold;
                shootsRemaining = 1;
                break;
            case GO_TO_EXIT:
                playerPosition = playerPositionWhenWumpusIsDead;
                finalScore = scoreWhenKilledWumpus;
                break;
        }
    }

    private Direction findDirectionTo(Coordinate target) {
        ArrayList<Direction> directions = wumpusWorld.getDirections(playerPosition);
        return directions.stream().filter(d -> d.getCoordinate() != null && d.getCoordinate().equals(target)).findFirst().orElse(null);
    }

    private void movePlayer(Direction direction) throws Exception {
        if (direction != null) {
            wumpusWorld.movePlayer(direction);
            playerPosition = direction.getCoordinate();
        }
    }

    private void printSummary() {
        System.out.println("\n\n--- GAME SUMMARY ---");
        System.out.println("WUMPUS DEAD: " + wumpusDead);
        System.out.println("GOLD TAKEN: " + goldHasBeenTaken);
        System.out.println("FINAL SCORE: " + finalScore);
        System.out.println("--------------------");
        System.out.println("Q-Table Weigths for take gold learning:");
         takeGoldTableQ.printWeightsTable();
        System.out.println("Q-Table Weigths for kill wumpus learning:");
         killWumpusTableQ.printWeightsTable();
        System.out.println("Q-Table Weigths to exit learning:");
         goToExitTableQ.printWeightsTable();
    }
}