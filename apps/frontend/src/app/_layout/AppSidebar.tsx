"use client"

import * as React from "react"
import Image from "next/image"
import Link from "next/link"
import NavData from "./navigation-data"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import NavMain from "./NavMain"
import NavSecondary from "./NavSecondary"

const AppSidebar = ({ ...props }: React.ComponentProps<typeof Sidebar>) => {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-2 h-14">
              <Link href="/">
                <Image
                  src="/logo/full_logo.webp"
                  alt="OSIPI Logo"
                  className="inline dark:hidden"
                  width={250}
                  height={72}
                />

                 <Image
                  src="/logo/full_logo_white.webp"
                  alt="OSIPI Logo"
                  className="hidden dark:inline"
                  width={250}
                  height={72}
                />
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        {/* CONTENT HERE  */}

        <NavMain items={NavData.navMain} />
        <NavSecondary items={NavData.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
       
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
