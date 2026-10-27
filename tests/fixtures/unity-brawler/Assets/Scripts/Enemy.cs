using UnityEngine;

public class Enemy : MonoBehaviour
{
    [SerializeField] private int health = 30;
    [SerializeField] private AudioSource audioSource;
    [SerializeField] private AudioClip hurtClip;

    public void TakeDamage(int damage)
    {
        health -= damage;
        audioSource.PlayOneShot(hurtClip);
        if (health <= 0)
        {
            Die();
        }
    }

    private void Die()
    {
        Destroy(gameObject);
    }
}
