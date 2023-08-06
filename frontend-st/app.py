import json
import requests
import streamlit as st


class App:
    def __init__(self):
        st.set_page_config(page_title='Health Search', page_icon='⚕️', layout='wide', initial_sidebar_state='auto')

        if 'backend_health' not in st.session_state:
            st.session_state.baclend_health = {}
        if 'customer_message' not in st.session_state:
            st.session_state.customer_message = ""
        if "model_response" not in st.session_state:
            st.session_state.model_response = ""
        if "graphql_query" not in st.session_state:
            st.session_state.graphql_query = False
        if "show_product_detail" not in st.session_state:
            st.session_state.show_product_detail = False

    @staticmethod
    def get_backend_health() -> None:
        st.session_state.backend_health = requests.get("http://backend:8000/health").json()        

    @staticmethod
    def render_graphql_query() -> None:
        graphql_query = st.expander('GraphQL Query', expanded=False)
        st.session_state.graphql_query = graphql_query.code(st.session_state.model_response.json()['query'])
    
    @staticmethod
    def render_generated_product_summary() -> None:
        st.markdown("✨ Generated Product Summary: " + st.session_state.model_response.json()['generative_summary'])

    @staticmethod
    def render_product_details(i: int) -> None:
        product = st.session_state.model_response.json()['results'][i]
        st.markdown("📝 Description:" + product['description'])
        st.markdown("🍏 Ingredients:" + product['ingredients'])
        st.markdown("📏 Distance: " + str(product['distance']))
        for j in range(min(3, len(product['reviews']))):  
            r = product['reviews'][j].replace("<span className='annotation'>", "<span style='color:red'>")
            st.markdown(r, unsafe_allow_html=True)

    def render_supplement_card(self, i: int) -> None:
        card = st.container()
        try:
            with card:
                product = st.session_state.model_response.json()['results'][i]
                st.markdown("""<hr style='border:2px solid grey'>""", unsafe_allow_html=True)
                st.text(product["brand"])
                st.markdown("**" + product["name"] + "**", unsafe_allow_html=True)
                st.image(product["image"], width=300)
                stars = "⭐" * int(product["rating"])
                st.markdown(stars)
                st.markdown("🤖 **Generated Review Summary** " + product["summary"], unsafe_allow_html=True)
                if st.session_state.show_product_detail:
                    self.render_product_details(i)
                st.write('\n'*2)
        except IndexError:
            pass

    def main(self):
        self.get_backend_health()
        with st.sidebar:        
            st.sidebar.title("About")
            st.sidebar.info(
                "Welcome to the Streamlit version of Healthsearch!\n\n"
                "Converts natural language to a GraphQL query to search for "
                "supplements with specific health effects based on user-written "
                "reviews. The demo uses generative search to further enhance the "
                "results by providing product and review summaries..\n\n"
                "Check the original Weaviate Healtsearch code at "
                "https://github.com/weaviate/healthsearch-demo\n\n"
                "Edward Schmuhl (Weaviate) wrote a great blog about the Healthsearch demo "
                "at https://weaviate.io/blog/healthsearch-demo\n\n"
            )
            
            st.session_state.show_product_detail = st.sidebar.checkbox('Show Product Detail')
            st.write(f"Weaviate backend: {st.session_state.backend_health['message']}")
            st.write(f"Cached query count: {st.session_state.backend_health['cache_count']}")
        
        st.markdown("<h1 style='text-align: center; color: black;'>HealthSearch Powered by Weaviate and Streamlit</h1>", unsafe_allow_html=True)

        with st.form("Ask Me"):
            st.session_state.customer_message = st.text_input(
                label="Natural Language Query", 
                help=("Search for products with specific health effects based "
                      "on user-written reviews. Press Generate to create a "
                      "GraphQL Query. Use the generated query to retrieve a "
                      "list of products. Check Show Product Detail for more "
                      "information.")
            )

            submitted = st.form_submit_button("Generate")
            if submitted:
                st.session_state.model_response = requests.post("http://backend:8000/generate_query", data=json.dumps({"text": st.session_state.customer_message}))          

        if st.session_state.model_response:
            #st.write(st.session_state.model_response.json())
            self.render_graphql_query()
            self.render_generated_product_summary()
            for i in range(0, len(st.session_state.model_response.json()['results']), 3):
                c1, c2, c3 = st.columns((1, 1, 1))
                with c1:
                    self.render_supplement_card(i)
                with c2:
                    self.render_supplement_card(i+1)
                with c3:
                    self.render_supplement_card(i+2)


if __name__ == "__main__":
    app = App()
    app.main()