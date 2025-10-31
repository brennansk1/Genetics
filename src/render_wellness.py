import streamlit as st

from .utils import analyze_wellness_snps


def render_wellness_profile(dna_data):
    st.header("Module 4: Holistic Wellness & Trait Profile")
    st.write(
        "This module provides engaging insights into non-clinical traits related to lifestyle, nutrition, and fitness."
    )

    # Educational tooltips for technical terms
    st.subheader("Understanding Key Terms")
    with st.expander("Click to see beginner-friendly definitions of genetic terms"):
        st.write(
            "**rsID**: A unique identifier for a genetic variant, like a serial number for a specific change in your DNA."
        )
        st.write(
            "**Genotype**: Your specific combination of DNA letters at a particular location (e.g., AA, AG, GG)."
        )
        st.write(
            "**Gene**: A segment of DNA that acts like a recipe for making proteins your body needs."
        )
        st.write(
            "**Interpretation**: What your genotype might mean for your health or traits."
        )

    if st.button("Analyze Wellness & Traits"):
        with st.spinner("Analyzing your wellness SNPs..."):
            wellness_results = analyze_wellness_snps(dna_data)

        st.success("Analysis complete!")

        st.subheader("4.1. Nutritional Genetics Profile")
        for rsid, data in wellness_results.items():
            if data["name"] in [
                "Lactose Tolerance",
                "Caffeine Metabolism",
                "Vitamin B12",
                "Vitamin D",
            ]:
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                st.write(
                    f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}"
                )

        # Educational content for nutritional genetics
        st.subheader("What Does This Mean?")
        st.write(
            "**DNA as a Recipe Book Analogy**: Think of your DNA as a recipe book containing instructions for how your body processes nutrients. Some genetic variants are like typos in the recipe that can affect digestion speed or nutrient absorption. For example, lactose intolerance variants mean your body produces less lactase enzyme, like having a recipe that doesn't work well with dairy ingredients."
        )
        st.write(
            "Your genetic profile can influence how your body handles common nutrients and substances, potentially affecting your dietary needs and responses to foods."
        )

        st.subheader("Key Takeaways")
        st.info(
            """
        - **Lactose Tolerance**: If you have variants associated with lactose intolerance, you might benefit from lactase supplements or lactose-free dairy products
        - **Caffeine Metabolism**: Your genotype can affect how quickly you process caffeine, influencing your sensitivity to coffee, tea, and energy drinks
        - **Vitamin Processing**: Genetic variants may mean you need more or less of certain vitamins from your diet or supplements
        - **Personalized Nutrition**: Understanding these variants helps you make informed choices about your diet and supplementation
        """
        )

        st.subheader("4.2. Fitness Genetics Profile")
        for rsid, data in wellness_results.items():
            if data["name"] == "Athletic Performance (Power/Sprint vs. Endurance)":
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                st.write(
                    f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}"
                )

        # Educational content for fitness genetics
        st.subheader("What Does This Mean?")
        st.write(
            "**Genetic Exercise Blueprint**: Your DNA influences whether you're naturally better suited for sprinting (power-based activities) or endurance activities (like long-distance running). This is like having a genetic predisposition for certain types of physical activities, but training and lifestyle still play major roles."
        )
        st.write(
            "While genetics provide a foundation, everyone can improve their fitness through consistent training, proper nutrition, and recovery."
        )

        st.subheader("Key Takeaways")
        st.info(
            """
        - **Power vs. Endurance**: Your genetics may suggest you're naturally inclined toward either explosive power activities or sustained endurance efforts
        - **Training Optimization**: Understanding your genetic profile can help tailor your exercise routine to your natural strengths
        - **Not Deterministic**: Genetics are just one factor - consistent training beats genetics over time
        - **Injury Prevention**: Knowing your genetic predispositions can help you train smarter and reduce injury risk
        """
        )

        st.subheader("4.3. Holistic Pathway Analysis")
        for rsid, data in wellness_results.items():
            if data["name"] == "Methylation (COMT)":
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                st.write(
                    f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}"
                )

        # Educational content for methylation
        st.subheader("What Does This Mean?")
        st.write(
            "**Methylation as Chemical Tags**: Think of methylation as adding chemical 'tags' to your DNA that can turn genes on or off. The COMT gene helps regulate these tags, affecting how your body processes stress, pain, and even certain nutrients. Variations can influence your sensitivity to caffeine and stress responses."
        )
        st.write(
            "Methylation is a fundamental process that affects many aspects of health, from detoxification to neurotransmitter regulation."
        )

        st.subheader("Key Takeaways")
        st.info(
            """
        - **Stress Response**: Your COMT genotype may influence how you respond to stress and caffeine
        - **Pain Sensitivity**: Genetic variations can affect how you perceive and process pain
        - **Detoxification**: Methylation pathways help your body process and eliminate toxins
        - **Holistic Health**: This pathway connects nutrition, stress management, and overall wellness
        """
        )

        st.subheader("4.4. 'Quirky' Trait Report")
        for rsid, data in wellness_results.items():
            if data["name"] in [
                "Bitter Taste Perception",
                "Photic Sneeze Reflex",
                "Asparagus Metabolite Detection",
            ]:
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                st.write(
                    f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}"
                )

        # Educational content for quirky traits
        st.subheader("What Does This Mean?")
        st.write(
            "**Genetic Quirks as Unique Features**: These traits show how genetics can influence everyday experiences that make you uniquely you. From how food tastes to reflex reactions, these variants highlight the diversity of human genetic variation."
        )
        st.write(
            "While these traits are 'quirky,' they demonstrate how genetics influence our sensory experiences and automatic responses."
        )

        st.subheader("Key Takeaways")
        st.info(
            """
        - **Taste Perception**: Genetic variants can make some bitter foods taste more or less intense to you
        - **Reflexes**: The photic sneeze reflex (sneezing in bright light) has a genetic component
        - **Sensory Experiences**: Genetics influence how we perceive smells, tastes, and environmental stimuli
        - **Human Diversity**: These traits remind us that genetic variation contributes to our unique individual experiences
        """
        )
