import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import execute_code

st.title("Test Plots Python Code Snippet")

# Sample DataFrame for demonstration
data = {
    'nombre del producto': ['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E', 'Producto F'],
    'categoría': ['gato', 'gato', 'perro', 'gato', 'perro', 'gato'],
    'best for pets precio final': [10.99, 15.49, 8.99, 20.00, 13.25, 18.75]
}
df = pd.DataFrame(data)
st.write("Sample DataFrame:")
st.dataframe(df)

# Input for the code snippet
code_snippet = st.text_area("Enter your code snippet:", """```python
df_gatos = df[df['categoría'] == 'gato'].copy()
df_gatos_sorted = df_gatos.sort_values(by=['best for pets precio final'], ascending=False)
top_5_gatos = df_gatos_sorted.head(5)

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(top_5_gatos['nombre del producto'], top_5_gatos['best for pets precio final'])
plt.xlabel('Nombre del Producto')
plt.ylabel('Precio Final')
plt.title('Top 5 Productos para Gatos')
plt.grid(True)
plt.show()
```""")


# Button to execute the code
if st.button("Execute Code"):
    # Execute the stripped code and capture the result
    local_vars, output = execute_code(code_snippet, df)

    # Display the captured output from print statements
    st.write("Captured Output:")
    st.text(output)

    # Display the plot
    if 'plt' in local_vars:
        st.write("Generated Plot:")
        st.pyplot(local_vars['plt'].gcf())

    # Optionally, display the resulting DataFrame if created
    if 'top_5_gatos' in local_vars:
        st.write("Top 5 Gatos DataFrame 'top_5_gatos':")
        st.dataframe(local_vars['top_5_gatos'])