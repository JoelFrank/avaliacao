public class Direction {
    public Direction(String name, Coordinate coordinate) {
        this.name = name;
        this.coordinate = coordinate;
    }

    private final String name;
    private final Coordinate coordinate;

    String getName() {
        return name;
    }

    Coordinate getCoordinate() {
        return coordinate;
    }
}
