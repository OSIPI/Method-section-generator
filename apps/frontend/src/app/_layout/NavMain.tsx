"use client"
import {TItems} from "@/types";

import {
    SidebarGroup,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar"
import Link from "next/link";
import { useAppContext } from "@/providers/AppProvider";
import { countErrorsAndWarnings } from "@/utils";
import { CountBadge } from "@/components/ui/count-badge";


const NavMain = ({items}: {items: TItems[]}) => {
    const { apiData } = useAppContext();
    const { errorCount, warningCount } = countErrorsAndWarnings(apiData);

    return (
        <SidebarGroup>
            <SidebarGroupContent className="flex flex-col gap-2">
                <SidebarMenu>
                    {items.map((item) => (
                        <SidebarMenuItem key={item.title}>
                            <SidebarMenuButton asChild>
                               <Link href={item.url} className="flex items-center gap-2">
                                   {item.icon && <item.icon/>}
                                   <span>{item.title}</span>
                                   {item.showCount && item.countType === "errors" && (
                                       <CountBadge count={errorCount} type={"error"} />
                                   )}
                                   {item.showCount && item.countType === "warnings" && (
                                       <CountBadge count={warningCount} type={"warn"} />
                                   )}
                                </Link>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    ))}
                </SidebarMenu>
            </SidebarGroupContent>
        </SidebarGroup>
    )
}


export default NavMain