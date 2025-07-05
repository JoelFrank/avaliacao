public class Coordinate {
    public Coordinate(int x, int y) {
        this.x = x;
        this.y = y;
    }

    private int x;
    private int y;

    public int getX() {
        return this.x;
    }

    public int getY() {
        return this.y;
    }

    @Override
    public String toString() {
        return "(" + x + ", " + y + ")";
    }

    @Override
    public boolean equals(Object obj) {
        if (obj instanceof Coordinate) {
            return ((Coordinate) obj).getX() == x && ((Coordinate) obj).getY() == y;
        }

        return false;
    }
}
