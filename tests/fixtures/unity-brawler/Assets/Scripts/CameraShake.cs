using UnityEngine;

public class CameraShake : MonoBehaviour
{
    public float magnitude = 0.5f;

    private void Update()
    {
        transform.localPosition = Random.insideUnitSphere * magnitude;
    }

    public void Shake(float amount)
    {
        magnitude = amount;
    }
}
