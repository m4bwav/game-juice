public class BuildingTests
{
    public void TakeDamage_ReducesHp()
    {
        var b = new Building();
        b.TakeDamage(3);
    }
}
