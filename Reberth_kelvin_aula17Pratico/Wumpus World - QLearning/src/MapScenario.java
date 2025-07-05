import org.jetbrains.annotations.Nullable;

public class MapScenario {
    public MapScenario(Coordinate coordinate){
        this.coordinate = coordinate;
        this.wumpus = false;
    }

    private Coordinate coordinate;
    private MapScenario parent;
    private boolean wumpus;
    private boolean pit;
    private boolean gold;

    public String getName() {
//        return "[ x: " + x + ", y: " + y + " Depth to gold: " + this.depthToGold + " Has gold: " + gold + " Has pit: " + pit + " Has Wumpus: " + wumpus + " ]";
        return "[ x: " + coordinate.getX() + ", y: " + coordinate.getY() + " ]";
    }

    public Coordinate getCoordinate() {
        return this.coordinate;
    }

    public void setWumpus(boolean wumpus) {
        this.wumpus = wumpus;
    }

    public boolean hasWumpus() {
        return this.wumpus;
    }

    public boolean hasPit() {
        return this.pit;
    }

    public void setPit(boolean pit) {
        this.pit = pit;
    }

    public boolean isExit() {
        return coordinate.getX() == 0 && coordinate.getY() == 0;
    }

    @Nullable
    public MapScenario getParent() {
        return this.parent;
    }


    public boolean hasGold() {
        return this.gold;
    }

    public void setGold(boolean gold) {
        this.gold = gold;
    }

}
