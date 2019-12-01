import React, { useState } from 'react'
import { Navbar, NavbarBrand } from 'reactstrap'

import styles from './Navbar.module.css';


const CustomNavbar = () => {

    return (
        <div>
            <Navbar className={styles.navbar} color="light" light expand="md">
                <NavbarBrand className={styles.navbrand}>
                    <h1>UFC Fight Predictor</h1>
                </NavbarBrand>
            </Navbar>
        </div>
    )

}

export default CustomNavbar