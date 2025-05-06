library(tidymodels)

full_data <- readRDS("market_cap_fundamentals.RDS")

# Drop non-predictive variables
model_data <- full_data %>%
  select(-ticker, -contains("_date")) %>%
  drop_na()

# 80/20 split
set.seed(42)
split <- initial_split(model_data, prop = 0.8)
train_data <- training(split)
test_data  <- testing(split)

# Define recipe
lm_rec <- recipe(market_cap ~ ., data = train_data) %>%
  step_zv(all_predictors()) %>%
  step_normalize(all_numeric_predictors())

# Define linear model spec
lm_mod <- linear_reg() %>%
  set_engine("lm")

# Combine in a workflow
lm_wf <- workflow() %>%
  add_model(lm_mod) %>%
  add_recipe(lm_rec)

# Fit model
lm_fit <- fit(lm_wf, data = train_data)

saveRDS(lm_fit, file = "~/PROJECT/Financials_Analysis/predict_market_cap/linreg/lm_fundamentals_market_cap_model.rds")

# Predict on test data
lm_preds <- predict(lm_fit, new_data = test_data) %>%
  bind_cols(test_data %>% select(market_cap))

# Evaluate performance
metrics(lm_preds, truth = market_cap, estimate = .pred)
