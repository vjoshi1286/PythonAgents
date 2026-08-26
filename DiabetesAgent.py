import os
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from excel_analyzer import analyze_blood_sugar_excel

@tool
def calculate_hba1c_from_glucose(avg_glucode_mg_dl: float) -> str:
   """ Calculates the estimated HbA1C percent from an average
       Blood glucose value in mg/dL 
       Use this whenever a user provides their average glucose or
       blood sugar and wants an HbA1c estimation
   """
   try:
      hba1c = (avg_glucode_mg_dl + 46.7)/28.7
      hba1c_round = round(hba1c,1)
     
      if hba1c_round < 5.7:
         status = "Normal"
      elif 5.7 <= hba1c_round <= 6.4:
         status = "Prediabetes"
      else:
         status = "Diabetes Mallitus"
     
      return f"Estimated HbA1c is {hba1c_round}% ({status})."
   
   except Exception as e:
      return f"Error calculating HbA1c: {str(e)}"

@tool
def calculate_bmi_and_risk(weight_kg: float, height_meters: float) -> str:
    """Calculates Body Mass Index (BMI) and evaluates Type 2 Diabetes screening risk.
    Expects 'weight_kg' and 'height_meters'. 
    Use this if a user asks about their weight, BMI, or if their weight increases diabetes risk.
    """
    try:
        if height_meters <= 0 or weight_kg <= 0:
            return "Weight and height must be greater than zero."
            
        bmi = weight_kg / (height_meters ** 2)
        bmi_round = round(bmi, 1)
        
        # ADA screening risk criteria
        if bmi_round < 18.5:
            status = "Underweight"
            risk = "Low baseline weight risk, but check for nutritional health."
        elif 18.5 <= bmi_round <= 24.9:
            status = "Normal weight"
            risk = "Standard baseline risk."
        elif 25.0 <= bmi_round <= 29.9:
            status = "Overweight"
            risk = "Increased risk for Type 2 Diabetes. ADA recommends screening if other risk factors are present."
        else:
            status = "Obese"
            risk = "High risk for Type 2 Diabetes. Screening is highly recommended by clinical standards."
            
        return f"Calculated BMI is {bmi_round} ({status}). ADA Risk Assessment: {risk}"
    except Exception as e:
        return f"Error calculating BMI: {str(e)}"

#Initialize the llm bind tools
# Use a system prompt to guide medical safety boudaries

llm = ChatOllama(model = "llama3.2", temperature=0.2)

tools= [calculate_hba1c_from_glucose, calculate_bmi_and_risk, analyze_blood_sugar_excel]

#Pull a standardized prompt template from Langchain hub
#This prompt structure expects 'tools' and 'agent_scratchpad'
#variables   	
system_instructions = (
    "You are a helpful medical assistant agent. "
    "You can calculate HbA1c using your tools when a user provides their blood glucose value. "
    "For symptom queries, rely on your general medical knowledge to explain them. "
    "from Excel logs when a user provides a spreadsheet file path as an input "
    "ALWAYS include a disclaimer that you are an AI and not a doctor and its all based on judgment"
    "A professional doctor will take the final call"
)

agent = create_agent(model=llm, tools=tools, system_prompt=system_instructions)

def run_agent_loop():
    print("Self contained Langchain Diabetes assistant agent initialized.")
    print("Ask questions like: 'My average blood sugar is 140, what is my HbA1c?' or 'What causes frequent urination?'")
    print("Type 'exit' to quit. \n")

    while True:
       user_input = input ("You: ")
   
       if user_input.lower().strip() == "exit":
         print("Shutting down the Agent. Stay Healthy!!!")
         break
   
       if not user_input.strip():
         continue

       try:
          # Invoke the modern agent direct wrapper natively using messages array formats
          response = agent.invoke(
                 {
                "messages": [
                    { "role": "user", "content": user_input}
                  ]
          })
          
          final_reply = response["messages"][-1].content
          print(f"\nAgent: {final_reply}\n" + "-"*40)

       except Exception as e:
          print(f"\nAn Error occured: {e}\n")

if __name__ == "__main__":
    run_agent_loop() 

