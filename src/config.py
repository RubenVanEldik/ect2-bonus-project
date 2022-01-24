import streamlit as st


def initialize():
    st.set_page_config(
        page_title="ECT2 - Bonus Project",
        page_icon="🌤️",
        menu_items={"Get Help": None, "Report a bug": None, "About": None,},
    )

    st.title("Bonus Project")
    st.markdown(
        """
        This website is an interactive model of a hybrid energy park which will be located in the north of Goeree-Overflakkee Island between Middelharnis and Stad aan ’t Haringvliet.

        The controls in the left sidebar allow you to change the amount of wind and solar PV capacity as well as the amount of battery storage. The model will rerun every time an input is changed.

        The source code for the model can be found on [Github](https://github.com/RubenVanEldik/ect2-bonus-project).
        """
    )
