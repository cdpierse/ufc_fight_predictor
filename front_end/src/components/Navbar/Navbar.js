import React from 'react'
import { Navbar, NavbarBrand } from 'reactstrap'

import styles from './Navbar.module.css';


const CustomNavbar = () => {

    return (
        <div>
            <Navbar className={styles.navbar} color= {styles.navbar} light expand="md">
                <NavbarBrand className={styles.navbrand}>
                    <h1 className="navTitle">UFC Fight Predictor</h1>
                </NavbarBrand>
            </Navbar>
        </div>
    )

}

export default CustomNavbar