using System.Collections;
using UnityEngine;

// Tuned counterpart: hit-stop shrinks when hits come fast, run clip speed follows ground speed.
public class Hero : MonoBehaviour
{
    [SerializeField] float moveSpeed = 6f;
    [SerializeField] float attackCooldown = 0.2f;
    [SerializeField] float hitStopDuration = 0.08f;
    [SerializeField] float clipStrideSpeed = 5f;

    Animator animator;
    CharacterController body;
    float lastHitTime = -10f;

    void Awake()
    {
        animator = GetComponent<Animator>();
        body = GetComponent<CharacterController>();
    }

    void Update()
    {
        var input = new Vector3(Input.GetAxis("Horizontal"), 0f, Input.GetAxis("Vertical"));
        var velocity = input * moveSpeed;
        body.Move(velocity * Time.deltaTime);
        animator.SetFloat("Speed", velocity.magnitude);
        animator.speed = velocity.magnitude > 0.1f ? Mathf.Clamp(velocity.magnitude / clipStrideSpeed, 0.8f, 1.25f) : 1f;
    }

    public void OnSwordHit(Enemy enemy)
    {
        enemy.TakeDamage(10);
        StartCoroutine(HitStop());
    }

    IEnumerator HitStop()
    {
        // Back-to-back hits get a shorter freeze so a fast sword does not stutter.
        float sinceLastHit = Time.unscaledTime - lastHitTime;
        lastHitTime = Time.unscaledTime;
        float freeze = sinceLastHit < attackCooldown * 2f ? hitStopDuration * 0.25f : hitStopDuration;
        Time.timeScale = 0f;
        yield return new WaitForSecondsRealtime(freeze);
        Time.timeScale = 1f;
    }
}
