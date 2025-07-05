import java.util.ArrayList;

public class WumpusWorld {
    public WumpusWorld() {
        int mapSize = 6;
        int pitCount = 3;

        graph = new MapGraph();
        initiateGraph(graph, mapSize);
        spawnWumpus(graph, mapSize);
        spawnPits(graph, mapSize, pitCount);
        spawnGold(graph, mapSize);
    }

    private final MapGraph graph;

    public void movePlayer(Direction direction) throws Exception {

        if (direction == null) {
            throw new Exception("WRONG COORDINATE TO MOVE");
        }

//        System.out.println("MOVING TO -> " + direction.getName());
        MapScenario nextScenario = graph.getNodeByCord(direction.getCoordinate());

        if (nextScenario.hasWumpus()) {
            throw new Exception("WUMPUS!");
        }

        if (nextScenario.hasPit()) {
            throw new Exception("PIT!");
        }

    }

    public void shootWumpus(Direction direction) throws Exception {
        if (direction == null) {
            throw new Exception("WRONG COORDINATE TO SHOOT WUMPUS!");
        }

        MapScenario scenario = graph.getNodeByCord(direction.getCoordinate());

        if (!scenario.hasWumpus()) {
            throw new Exception("YOU MISSED THE SHOOT!");
        }

        scenario.setWumpus(false);
    }

    public boolean hasGold(Coordinate currentCoordinate) {
        MapScenario scenario = graph.getNodeByCord(currentCoordinate);

        return scenario.hasGold();
    }

    public void takeGold(Coordinate currentCoordinate) throws Exception {
        if (!hasGold(currentCoordinate)) {
            throw new Exception("GOLD IS NOT HERE!");
        }

        MapScenario scenario = graph.getNodeByCord(currentCoordinate);
        scenario.setGold(false);
    }

    public boolean isExit(Coordinate coordinate) {
        return coordinate.equals(new Coordinate(0, 0));
    }

    public ArrayList<Direction> getDirections(Coordinate currentCoordinate) {
        MapScenario currentScenario = graph.getNodeByCord(currentCoordinate);
        return graph.getDirectionsForNode(currentScenario);
    }

    public MapGraph getGraph() {
        return this.graph;
    }

    private void initiateGraph(MapGraph graph, int mapSize) {
        for (int x = 0; x < mapSize; x++) {
            MapScenario scenario = new MapScenario(new Coordinate(x, 0));
            MapScenario previousScenario = scenario;

            graph.addVertice(scenario);

            for (int y = 1; y < mapSize; y++) {
                MapScenario topScenario = graph.getNodeByCord(new Coordinate(x - 1, y));

                MapScenario parentScenario = new MapScenario(new Coordinate(x, y));

                graph.addVertice(parentScenario);

                ///  Left <> Right
                graph.linkupVertices(previousScenario, parentScenario);
                graph.linkupVertices(parentScenario, previousScenario);

                ///  Top <> Bottom
                if (topScenario != null) {
                    graph.linkupVertices(parentScenario, topScenario);
                    graph.linkupVertices(topScenario, parentScenario);
                }

                previousScenario = parentScenario;
            }

            ///  First column connections
            MapScenario topScenario = graph.getNodeByCord(new Coordinate(x - 1, 0));

            if (topScenario != null) {
                graph.linkupVertices(scenario, topScenario);
                graph.linkupVertices(topScenario, scenario);
            }
        }
    }

    private void spawnWumpus(MapGraph graph, int mapSize) {
        boolean wumpusPlaced = false;

        do {
            int x = (int) Math.round(mapSize/2.0);
            int y = (int) Math.round(mapSize/2.0);

            MapScenario targetScenario = graph.getNodeByCord(new Coordinate(x, y));

            if (targetScenario != null && !targetScenario.hasPit() && (x != 0 && y != 0)) {
                targetScenario.setWumpus(true);
                wumpusPlaced = true;
            }
        } while (!wumpusPlaced);
    }

    private void spawnPits(MapGraph graph, int mapSize, int pitCount) {
        double[] pitPositions = {mapSize/1.5, mapSize/2.5, mapSize/3.5};
        for (double position : pitPositions) {
            int x = (int) Math.round(position);
            int y = (int) Math.round(position);

            MapScenario targetScenario = graph.getNodeByCord(new Coordinate(x, y));

            if (targetScenario != null && !targetScenario.hasWumpus() && (x != 0 && y != 0)) {
                targetScenario.setPit(true);
                pitCount--;
            }
        }
    }

    private void spawnGold(MapGraph graph, int mapSize) {
        boolean goldWasSpawned = false;
        do {
            int x = (int) Math.round(mapSize-1.0);
            int y = (int) Math.round(mapSize-1.0);

            MapScenario targetScenario = graph.getNodeByCord(new Coordinate(x, y));

            if (targetScenario != null && !targetScenario.hasWumpus() && !targetScenario.hasPit() && (x != 0 && y != 0)) {
                targetScenario.setGold(true);
                goldWasSpawned = true;
            }

        } while (!goldWasSpawned);
    }
}
