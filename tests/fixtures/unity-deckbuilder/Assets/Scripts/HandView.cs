using System.Collections;
using UnityEngine;

// A card hand view: plays, draws and ends turns with no feedback yet.
public class HandView : MonoBehaviour
{
    public Deck deck;

    public void OnCardPlayed(Card card, int slot)
    {
        RefreshHand();
    }

    IEnumerator AnimateSingleDraw(Card card)
    {
        hand.Add(card);
        yield return null;
    }

    public void OnTurnEnded(int turn)
    {
        RefreshHand();
    }

    public bool HasPendingDamageReveal(Building b)
    {
        return b != null && b.hp < b.maxHp;
    }

    void RefreshHand() { }
}
