import pandas as pd
import matplotlib.pyplot as plt

import blackjack as bj

##
# Running the Simulation
##

SEED = 192
N_ROUNDS = 1_000_000

results = []
stand_values = list(range(14,21))

# For reproducing results.
bj.set_seed(SEED)

# Play a number of rounds and store the results.
# For every N_ROUNDS number of games feed the next in 'stand_values' to the simulator.
for stand_value in stand_values:
    for n in range(N_ROUNDS):
        game = bj.play_round(stand_value)

        results.append({
            'round': n + 1,
            'stand_value': stand_value,
            'player_total': bj.sum_hand(game['player_hand']), # For future use.
            'dealer_total': bj.sum_hand(game['dealer_hand']), # For future use.
            'dealer_upcard': game['dealer_hand'][0],
            'outcome': game['outcome']
        })


##
# Manipulate the Results
##

# Convert results into a DataFrame.
results_df = pd.DataFrame(results)

# Save results.
results_df.to_csv("results.csv", index=False)

# Calculate cumulative profit.
results_df = results_df.assign(
    cumulative_profit=results_df.groupby('stand_value')['outcome'].cumsum()
)

# Determine percentage of games won for a given stand_value and dealer_upcard.
# Organise into a new DataFrame.
won_df = (
    results_df
    .assign(won=results_df['outcome'] == 1) # Set wins to true, losses and draws are false.
    .groupby(['stand_value', 'dealer_upcard'])['won']
    .mean()
    .mul(100)
    .reset_index(name='percentage_won')
)

# Display dealer_upcard in correct order.
won_df['dealer_upcard'] = pd.Categorical(won_df['dealer_upcard'], categories=bj.VALUES, ordered=True)
won_df = won_df.sort_values(by='dealer_upcard')

# Save results.
won_df.to_csv("won.csv", index=False)


##
# Plotting Results
##

# Visualise simulated profit and loss.
fig1, ax1 = plt.subplots()
# Produce a line for each stand value.
for stand_value in stand_values:
    ax1.plot(
        results_df[results_df['stand_value'] == stand_value]['round'],
        results_df[results_df['stand_value'] == stand_value]['cumulative_profit'],
        label=f'Stand Value: {stand_value}'
    )

# Decorate plot.
ax1.set_title(f'Cumulative Profit Across {N_ROUNDS} Rounds')
ax1.set_xlabel('Rounds Played')
ax1.set_ylabel('Cumulative Profit')
ax1.grid(alpha=0.3)
ax1.legend()


# Visualise how the dealer's upcard effects % of games won for given stratergy.
won_heatmap_df = won_df.pivot(
    index='stand_value',
    columns='dealer_upcard',
    values='percentage_won'
)

fig, ax2 = plt.subplots()
im = ax2.imshow(won_heatmap_df, cmap='winter')

# Decorate plot.
ax2.set_xticks(range(len(won_heatmap_df.columns)), labels=won_heatmap_df.columns)
ax2.set_yticks(range(len(won_heatmap_df.index)), labels=won_heatmap_df.index)

ax2.set_title('Percentage of Games Won by Stand Value and Dealer Upcard')
ax2.set_xlabel('Dealer Upcard')
ax2.set_ylabel('Stand Value')

fig.colorbar(im, ax=ax2, label='Percentage of Games Won')

plt.show()

print(won_heatmap_df)
