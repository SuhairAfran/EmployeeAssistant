# visualize.py
from app.graph.workflow import workflow

def visualize_graph():
    # 1. Generate and print the ASCII Graph
    print("\nEnterprise AI Copilot LangGraph Flow:\n")
    try:
        ascii_graph = workflow.get_graph().draw_ascii()
        print(ascii_graph)
    except Exception as e:
        print(f"Could not draw ASCII graph: {e}")

    # 2. Generate and save the PNG Graph
    try:
        png_data = workflow.get_graph().draw_mermaid_png()
        
        with open("enterprise_copilot_graph.png", "wb") as file:
            file.write(png_data)
            
        print("\n✅ Graph successfully saved as 'enterprise_copilot_graph.png'")
    except Exception as e:
        print(f"\n❌ Could not save PNG: {e}")

if __name__ == "__main__":
    visualize_graph()