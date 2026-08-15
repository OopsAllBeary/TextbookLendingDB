
def parse_bookstore_response(data):

    print(
        "PARSER DATA TYPE:",
        type(data)
    )

    materials = []


    # BKSTR returns a list at the top level.
    if not isinstance(
        data,
        list
    ):

        print(
            "Unexpected bookstore response format."
        )

        return materials


    for bookstore_result in data:

        if not isinstance(
            bookstore_result,
            dict
        ):
            continue


        requirement_labels = (
            bookstore_result.get(
                "requirementTypeLabelMap",
                {}
            )
        )


        course_sections = (
            bookstore_result.get(
                "courseSectionDTO",
                []
            )
        )


        if not isinstance(
            course_sections,
            list
        ):
            continue


        for course_section in course_sections:

            if not isinstance(
                course_section,
                dict
            ):
                continue


            course_materials = (
                course_section.get(
                    "courseMaterialResultsList",
                    []
                )
            )


            if not isinstance(
                course_materials,
                list
            ):
                continue


            for raw_material in course_materials:

                if not isinstance(
                    raw_material,
                    dict
                ):
                    continue


                # ---------------------------------
                # Determine actual materials
                # ---------------------------------

                nested_materials = raw_material.get(
                    "allMaterials"
                )


                if (
                    isinstance(
                        nested_materials,
                        list
                    )
                    and nested_materials
                ):

                    materials_to_process = (
                        nested_materials
                    )

                else:

                    materials_to_process = [
                        raw_material
                    ]


                # ---------------------------------
                # Process each material
                # ---------------------------------

                for actual_material in materials_to_process:

                    if not isinstance(
                        actual_material,
                        dict
                    ):
                        continue


                    requirement_type = (
                        actual_material.get(
                            "requirementType"
                        )
                        or raw_material.get(
                            "requirementType"
                        )
                        or ""
                    )


                    requirement_label = (
                        requirement_labels.get(
                            requirement_type,
                            requirement_type
                        )
                    )

                    department = (
                        course_section.get("department")
                        or course_section.get("departmentName")
                        or course_section.get("departmentDescriptorCode")
                        or ""
                    ).strip()

                    course_number = (
                        course_section.get("course")
                        or course_section.get("courseName")
                        or course_section.get("courseDescriptorCode")
                        or ""
                    ).strip()

                    course_display = (
                        f"{department} {course_number}"
                    ).strip()


                    material = {

                        # ---------------------------------
                        # COURSE INFORMATION
                        # ---------------------------------

                        "course": course_display,

                        "course_id": (
                            course_section.get(
                                "courseId"
                            )
                            or ""
                        ),

                        "campus": (
                            course_section.get(
                                "campusName"
                            )
                            or ""
                        ),


                        # ---------------------------------
                        # MATERIAL INFORMATION
                        # ---------------------------------

                        "title": (
                            actual_material.get(
                                "title"
                            )
                            or ""
                        ),

                        "author": (
                            actual_material.get(
                                "author"
                            )
                            or ""
                        ),

                        "edition": (
                            actual_material.get(
                                "edition"
                            )
                            or ""
                        ),

                        "isbn": (
                            actual_material.get(
                                "isbn"
                            )
                            or actual_material.get(
                                "isbnDisplay"
                            )
                            or ""
                        ),

                        "publisher": (
                            actual_material.get(
                                "publisher"
                            )
                            or ""
                        ),

                        "material_type": (
                            actual_material.get(
                                "materialType"
                            )
                            or ""
                        ),

                        "requirement_type":
                            requirement_type,

                        "requirement_label":
                            requirement_label,

                        "included_material": (
                            actual_material.get(
                                "includEDMaterialFlag",
                                actual_material.get(
                                    "includedMaterial",
                                    False
                                )
                            )
                        ),

                        "is_package": (
                            actual_material.get(
                                "isPackage",
                                False
                            )
                        ),

                        "price_range": (
                            actual_material.get(
                                "priceRangeDisplay"
                            )
                            or ""
                        ),

                        "image": (
                            actual_material.get(
                                "bookImage"
                            )
                            or ""
                        ),

                        "options": []
                    }


                    # ---------------------------------
                    # PURCHASE / RENTAL / DIGITAL OPTIONS
                    # ---------------------------------

                    raw_options = (
                        actual_material.get(
                            "printItemDTOs",
                            {}
                        )
                    )


                    if isinstance(
                        raw_options,
                        dict
                    ):

                        for (
                            option_type,
                            option_data
                        ) in raw_options.items():

                            if not isinstance(
                                option_data,
                                dict
                            ):
                                continue


                            price = _money_value(
                                option_data.get(
                                    "priceNumeric"
                                )
                            )


                            if price is None:

                                price = _money_value(
                                    option_data.get(
                                        "priceDisplay"
                                    )
                                )


                            option = {

                                "type":
                                    option_type,

                                "label":
                                    _option_label(
                                        option_type
                                    ),

                                "price":
                                    price,

                                "price_display": (
                                    option_data.get(
                                        "priceDisplay"
                                    )
                                    or ""
                                ),

                                "availability": (
                                    option_data.get(
                                        "inventoryStatusDB"
                                    )
                                    or option_data.get(
                                        "inventoryStatusBus"
                                    )
                                    or ""
                                ),

                                "binding": (
                                    option_data.get(
                                        "binding"
                                    )
                                    or ""
                                ),

                                "sku": (
                                    option_data.get(
                                        "skuPartNumber"
                                    )
                                    or ""
                                ),

                                "item_id": (
                                    option_data.get(
                                        "itemCatentryId"
                                    )
                                    or ""
                                ),

                                "preselected": (
                                    option_data.get(
                                        "preselected",
                                        False
                                    )
                                )
                            }


                            material[
                                "options"
                            ].append(
                                option
                            )


                    # ---------------------------------
                    # FALLBACK TO MATERIAL PRICE
                    # ---------------------------------

                    if not material["options"]:

                        fallback_price = _money_value(
                            actual_material.get(
                                "priceRangeDisplay"
                            )
                        )


                        if fallback_price is not None:

                            material[
                                "options"
                            ].append(
                                {
                                    "type": "DIGITAL",

                                    "label": "Digital",

                                    "price":
                                        fallback_price,

                                    "price_display":
                                        actual_material.get(
                                            "priceRangeDisplay"
                                        ),

                                    "availability": "",

                                    "binding": "",

                                    "sku": (
                                        actual_material.get(
                                            "productPartNumber"
                                        )
                                        or ""
                                    ),

                                    "item_id": (
                                        actual_material.get(
                                            "productCatentryId"
                                        )
                                        or ""
                                    ),

                                    "preselected": True
                                }
                            )


                    # ---------------------------------
                    # DETERMINE CATEGORY
                    # ---------------------------------

                    material[
                        "category"
                    ] = get_material_category(
                        material
                    )


                    materials.append(
                        material
                    )


    total_current_price = 0.0

    for material in materials:

        price = None

        options = material.get(
            "options",
            []
        )


        # ---------------------------------
        # Prefer preselected option
        # ---------------------------------

        for option in options:

            if option.get(
                "preselected"
            ):

                option_price = option.get(
                    "price"
                )

                if option_price is not None:

                    price = float(
                        option_price
                    )

                    break


        # ---------------------------------
        # Otherwise use first priced option
        # ---------------------------------

        if price is None:

            for option in options:

                option_price = option.get(
                    "price"
                )

                if option_price is not None:

                    price = float(
                        option_price
                    )

                    break


        material["current_price"] = price


        if price is not None:

            total_current_price += price


        print(
            "PRICE CHECK:",
            material.get("title"),
            "=>",
            price
        )


    print(
        f"Parsed {len(materials)} materials."
    )

    print(
        f"Total current price: ${total_current_price:.2f}"
    )

    return {
        "materials": materials,
        "total_current_price": total_current_price
    }



def _requirement_label(
    data,
    requirement_type
):

    labels = data.get(
        "requirementTypeLabelMap",
        {}
    )

    return labels.get(
        requirement_type,
        requirement_type or ""
    )



def _option_label(
    option_type
):

    labels = {

        "BUY_NEW":
            "Buy New",

        "BUY_USED":
            "Buy Used",

        "RENTAL_NEW":
            "Rent New",

        "RENTAL_USED":
            "Rent Used",

        "DIGITAL":
            "Digital"
    }


    return labels.get(
        option_type,
        option_type.replace(
            "_",
            " "
        ).title()
    )



def _money_value(value):

    if value is None:
        return None


    if isinstance(
        value,
        (int, float)
    ):
        return float(value)


    if isinstance(
        value,
        str
    ):

        value = value.replace(
            "$",
            ""
        ).replace(
            ",",
            ""
        ).strip()


        if not value:
            return None


        try:

            return float(
                value
            )

        except ValueError:

            return None


    return None



def get_material_category(material):

    material_type = (
        material.get(
            "material_type",
            ""
        )
        or ""
    ).upper()


    title = (
        material.get(
            "title",
            ""
        )
        or ""
    ).lower()


    if material.get(
        "included_material",
        False
    ):

        return "Included"


    if material.get(
        "is_package",
        False
    ):

        return "Package"


    if material_type in (
        "CEB",
        "DIGITAL"
    ):

        return "Digital"


    if any(
        word in title
        for word in (

            "access code",

            "online access",

            "digital access",

            "ebook",

            "e-book"

        )
    ):

        return "Digital"


    if material_type == "SUP":

        return "Supplement"


    if material_type == "TXT":

        return "Physical Book"


    return "Other"

def get_current_material_price(material):
    """
    Returns the price of the currently selected/preselected
    bookstore option for a material.
    """

    options = material.get(
        "printItemDTOs",
        {}
    )

    if not isinstance(options, dict):
        return None

    # First look for an explicitly preselected option.
    for option in options.values():

        if not isinstance(option, dict):
            continue

        if option.get("preselected") is True:
            return _money_value(
                option.get("priceNumeric")
            )

    # Some BKSTR responses use preSelected at the
    # material level instead, so fall back to the
    # first available numeric price.
    for option in options.values():

        if not isinstance(option, dict):
            continue

        price = _money_value(
            option.get("priceNumeric")
        )

        if price is not None:
            return price

    return None