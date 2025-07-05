import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.HashMap;

public class MapGraph {
    public MapGraph() {
        vertices = new HashMap<>();
    }

    private HashMap<MapScenario, ArrayList<MapScenario>> vertices;

    public void addVertice(MapScenario scenario) {
        vertices.putIfAbsent(scenario, new ArrayList<>());
    }

    public void linkupVertices(MapScenario node, MapScenario child) {
        ArrayList<MapScenario> children = vertices.getOrDefault(node, null);
        if (children == null) {
            return;
        }
        children.add(child);
    }

    public ArrayList<MapScenario> getEdges(MapScenario scenario) {
        return vertices.getOrDefault(scenario, new ArrayList<>());
    }

    @Nullable
    public MapScenario getNodeByCord(Coordinate coordinate) {
        MapScenario result = null;

        for (MapScenario scenario : vertices.keySet()) {
            Coordinate scenarioCoordinate = scenario.getCoordinate();
            if (coordinate.equals(scenarioCoordinate)) {
                result = scenario;
                break;
            }
        }
        return result;
    }

    public HashMap<MapScenario, ArrayList<MapScenario>> getVertices() {
        return this.vertices;
    }

    public ArrayList<Direction> getDirectionsForNode(MapScenario node) {
        ArrayList<Coordinate> neighbors = new ArrayList<>(getEdges(node).stream().map(MapScenario::getCoordinate).toList());
        Coordinate nodeCoordinate = node.getCoordinate();
        ArrayList<Direction> result = new ArrayList<>();

        Coordinate leftCoordinate = new Coordinate(nodeCoordinate.getX(), nodeCoordinate.getY() - 1);
        Coordinate rightCoordinate = new Coordinate(nodeCoordinate.getX(), nodeCoordinate.getY() + 1);
        Coordinate bottomCoordinate = new Coordinate(nodeCoordinate.getX() + 1, nodeCoordinate.getY());
        Coordinate topCoordinate = new Coordinate(nodeCoordinate.getX() - 1, nodeCoordinate.getY());

        result.add(new Direction("LEFT", neighbors.contains(leftCoordinate) ? leftCoordinate : null));
        result.add(new Direction("RIGHT", neighbors.contains(rightCoordinate) ? rightCoordinate : null));
        result.add(new Direction("BOTTOM", neighbors.contains(bottomCoordinate) ? bottomCoordinate : null));
        result.add(new Direction("TOP", neighbors.contains(topCoordinate) ? topCoordinate : null));

        return result;
    }

    public void printGraph() {
        for (MapScenario scenario : vertices.keySet()) {
            System.out.println(
                    scenario.getName() +
                            " -> " +
                            String.join(
                                    ", ",
                                    vertices.get(scenario).stream().map(MapScenario::getName).toList()
                            )
            );
        }
    }

    public void printGraphTree() {
        MapScenario root = getNodeByCord(new Coordinate(0, 0));

        printSubtree(root, 0);
    }

    private void printSubtree(MapScenario node, int level) {
        Coordinate coordinate = node.getCoordinate();
        System.out.println("  ".repeat(level) + level + "(" + coordinate.getX() + ", " + coordinate.getY() + ") Has gold: " + (node.hasGold() ? "\uD83E\uDD47" : "") + " Pit: " + (node.hasPit() ? "\uD83D\uDD73" : "" )+ " Wumpus: " + (node.hasWumpus() ? "\uD83D\uDC7E" : ""));

        for (MapScenario vertice : getVertices().keySet()) {
            MapScenario parent = vertice.getParent();
            if (parent == node) {
                printSubtree(vertice, level + 1);
            }
        }
    }

}
