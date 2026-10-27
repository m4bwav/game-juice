local CollectionService = game:GetService("CollectionService")

local function damageHumanoid(hit: BasePart)
	local humanoid = hit.Parent and hit.Parent:FindFirstChildOfClass("Humanoid")
	if humanoid then
		humanoid:TakeDamage(100)
	end
end

for _, lava in CollectionService:GetTagged("Lava") do
	lava.Touched:Connect(damageHumanoid)
end
