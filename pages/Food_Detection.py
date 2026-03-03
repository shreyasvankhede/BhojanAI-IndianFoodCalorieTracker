
import streamlit as st
from calorie_counter import User


# -------------------------
# 🔐 Require Login
# -------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.switch_page("front.py")
    st.stop()

if "manual_meal_type" not in st.session_state:
    st.session_state.manual_meal_type = None

if "camera_open" not in st.session_state:
    st.session_state.camera_open = False

user = User(st.session_state.username)
st.title("Log food")
# =========================================================
# (Search + Camera Button)
# =========================================================

col_search, col_cam = st.columns([5, 1])

with col_search:
    search_query = st.text_input(
        "",
        placeholder="Search food (e.g. dosa, paneer, idli...)",
        label_visibility="collapsed"
    )

with col_cam:
    if st.button("📷", use_container_width=True):
        st.session_state.camera_open = True

# =========================================================
# 📷 CAMERA MODE
# =========================================================

image_source = None

if st.session_state.get("camera_open", False):
    camera_image = st.camera_input("Take a picture")

    if camera_image:
        image_source = camera_image
        st.image(camera_image, use_container_width=True)

        with st.spinner("Detecting food..."):
            result = user.detect_food(image_source)

        if result:
            class_counts, detected_names = result

            if len(detected_names) > 0:
                st.write("Confirm detected foods")

                confirmed_items = []

                for idx, food in enumerate(class_counts.keys()):
                    suggestions = user.suggest_similar_foods(food)

                    corrected = st.selectbox(
                        f"{food}",
                        suggestions,
                        key=f"cam_name_{idx}"
                    )

                    qty = st.number_input(
                        "grams",
                        min_value=1,
                        max_value=1000,
                        value=100,
                        key=f"cam_qty_{idx}"
                    )

                    confirmed_items.append((corrected, qty))

                if st.button("Add Detected Meal"):
                    meal_type = user.create_meal()

                    for food, qty in confirmed_items:
                        user.add_food_to_meal(meal_type, food, qty)

                    st.success("Meal logged successfully!")
                    st.session_state.camera_open = False

            else:
                st.warning("No food detected.")

# =========================================================
# 🔎 LIVE SEARCH MODE
# =========================================================


# Create layout columns FIRST
col_food, col_qty ,col_meal= st.columns([2, 1,1])
col_food.space("small")
col_qty.space("small")
col_meal.space("small")
selected_food = None
qty = None
meal_type=None

if search_query:
    matches = user.suggest_similar_foods(search_query)

    if matches:
        # Put selectbox inside first column
        with col_food:
            selected_food = st.selectbox(
                "Matching items",
                matches,
                key="food_select"
            )
        # Put quantity box inside second column
        with col_qty:
            qty = st.number_input(
                min_value=0.1,
                max_value=1000.0,
                value=100.0,
                label="Quantity in grams",
                key="qty_input"
            )
        with col_meal:
            meal_type = st.selectbox(
                "Meal",
                ("Breakfast", "Lunch", "Dinner","Snacks"),
                index=None,
                placeholder="Select Meal type")
    else:
        st.warning("No matching foods found.")


if selected_food is not None:
    nutrition = user.get_food_info(selected_food)

    if nutrition is None:
        st.error("Food not found in database.")
    else:
        calories, carbs, protein, fats, sugar, fibre = nutrition

        st.subheader("Meal Summary per 100g")
        st.metric("Calories", f"{calories:.2f} kcal")
        st.write(f"Carbs: {carbs:.2f} g")
        st.write(f"Protein: {protein:.2f} g")
        st.write(f"Fats: {fats:.2f} g")
        st.write(f"Fibre: {fibre:.2f} g")
        st.write(f"Sugar: {sugar:.2f} g")

        
# Maintain active meal session

    if st.button("Add Food"):
        if selected_food:
            user.add_food_to_meal(meal_type, selected_food, qty)
            st.success(f"{selected_food} added!")

# =========================================================
# ✅ FINISH MEAL
# =========================================================

# if st.session_state.manual_meal_type:
#     if st.button("Finish Meal"):
#         meal_type = st.session_state.manual_meal_type

#         calories, carbs, protein, fats, fibre, sugar = user.calculate_meal_cals(meal_type)

#         st.subheader("Meal Summary")
#         st.metric("Calories", f"{calories:.2f} kcal")
#         st.write(f"Carbs: {carbs:.2f} g")
#         st.write(f"Protein: {protein:.2f} g")
#         st.write(f"Fats: {fats:.2f} g")
#         st.write(f"Fibre: {fibre:.2f} g")
#         st.write(f"Sugar: {sugar:.2f} g")

        


import streamlit as st

st.header("Logged Meals")

# -------------------------
# Daily Total
# -------------------------
daily_macros = user.calculate_daily_macros()
daily_cal = daily_macros[0]
st.metric("Today's Total Calories", f"{daily_cal:.2f} kcal")


# -------------------------
# Reusable Function For Each Meal
# -------------------------
def render_meal_section(meal_name):

    st.subheader(meal_name)

    meal_cals = user.calculate_meal_cals(meal_name)
    st.write(f"{meal_name} intake was {meal_cals[0]:.2f} kcal")

    df = user.get_meal_entries(meal_name)

    if df.empty:
        st.info("No entries logged.")
        return

    # Keep original copy
    original_df = df.copy()

    # -------------------------
    # Add Serial Number Column
    # -------------------------
    df = df.reset_index(drop=True)
    df.insert(0, "Sr No", df.index + 1)

    edited_df = st.data_editor(
        df,
        column_config={
            "Sr No": st.column_config.Column(disabled=True),
            "item_id": None,  # hide item_id completely
            "Name": st.column_config.Column(disabled=True),
            "calories": st.column_config.Column(disabled=True),
            "carbs": st.column_config.Column(disabled=True),
            "protein": st.column_config.Column(disabled=True),
            "fats": st.column_config.Column(disabled=True),
            "fibre": st.column_config.Column(disabled=True),
            "sugar": st.column_config.Column(disabled=True),
        },
        use_container_width=True,
        num_rows="dynamic",
        key=f"{meal_name}_editor"
    )

    # -------------------------
    # Handle Deletions
    # -------------------------
    deleted_ids = set(original_df["item_id"]) - set(edited_df["item_id"])

    for item_id in deleted_ids:
        user.change_entry(item_id, delete_entry=True)

    # -------------------------
    # Handle Quantity Updates
    # -------------------------
    for _, row in edited_df.iterrows():

        original_row = original_df[
            original_df["item_id"] == row["item_id"]
        ].iloc[0]

        if row["quantity_g"] != original_row["quantity_g"]:
            user.change_entry(
                row["item_id"],
                new_quantity=row["quantity_g"]
            )
            st.rerun()

    if deleted_ids:
        st.rerun()



render_meal_section("Breakfast")
render_meal_section("Lunch")
render_meal_section("Snacks")
render_meal_section("Dinner")