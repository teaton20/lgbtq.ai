def decide_branch():
    print("🤖 Evaluating which model to keep...")
    
    # Dummy logic — later replace with actual metric comparison
    new_model_is_better = False  # True or False
    
    if new_model_is_better:
        print("✅ Deploying new model")
        return "deploy_model"
    else:
        print("🛑 Keeping current model")
        return "keep_model"
