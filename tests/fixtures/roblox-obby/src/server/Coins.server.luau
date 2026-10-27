local Players = game:GetService("Players")
local CollectionService = game:GetService("CollectionService")

local function onPlayerAdded(player: Player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	leaderstats.Parent = player
	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Parent = leaderstats
end

local function collectCoin(coin: BasePart, player: Player)
	local coins = player.leaderstats.Coins
	coins.Value += 1
	coin:Destroy()
end

local function onCoinTouched(coin: BasePart, hit: BasePart)
	local player = Players:GetPlayerFromCharacter(hit.Parent)
	if player then
		collectCoin(coin, player)
	end
end

for _, coin in CollectionService:GetTagged("Coin") do
	coin.Touched:Connect(function(hit)
		onCoinTouched(coin, hit)
	end)
end

Players.PlayerAdded:Connect(onPlayerAdded)
