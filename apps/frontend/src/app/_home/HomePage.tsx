import {Card, CardContent} from "@/components/ui/card";

import UploadButtons from "@/app/_home/UploadButtons";
import WhatIsThisTool from "@/app/_home/WhatIsThisTool";
import HowToUseTheTool from "@/app/_home/HowToUseTheTool";


const HomePage = () => {
    return (
        <main className="flex flex-col gap-6 h-full w-full p-5">
            <section className="flex flex-col gap-4 flex-1">
                <h1 className="text-2xl font-bold">
                    Welcome to the OSIPI ASL Reporting Tool
                </h1>
                <Card className="h-full">
                    <CardContent className="flex flex-col gap-5">
                        <UploadButtons /> 
                        <WhatIsThisTool />
                        <hr/>
                        <HowToUseTheTool />
                    </CardContent>
                </Card>
            </section>
        </main>
    );
}



export default HomePage;