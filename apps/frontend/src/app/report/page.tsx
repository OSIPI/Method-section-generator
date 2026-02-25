"use client";
import MissingParameters from "@/app/report/_components/MissingParameters";
import BasicReport from "@/app/report/_components/BasicReport";
import ExtendedReport from "@/app/report/_components/ExtendedReport";
import CardWithTitle from "@/components/general/CardWithTitle";
import ParametersTable from "@/app/report/_components/ParametersTable";
import {useAppContext} from "@/providers/AppProvider";

export default function Home() {

    const {apiData} = useAppContext();

    if (!apiData.asl_parameters) {
        return <NoReport />;
    }

    return (
        <div className="flex gap-4 h-full w-full p-5 ">

            <div className={"w-2/5"}>
                <CardWithTitle title={"Parameters"} className={"h-2/3"}>
                    <ParametersTable/>
                </CardWithTitle>

                <CardWithTitle title={"Missing Parameters"} className={"h-1/3"}>
                    <MissingParameters/>
                </CardWithTitle>

            </div>

            <div className={"flex flex-col gap-4 ml-4 h-full w-3/5"}>

                <CardWithTitle title={"Basic Report"} className={"h-2/5"}>
                    <BasicReport/>
                </CardWithTitle>


                <CardWithTitle title={"Extended Report"} className={"h-3/5"}>
                    <ExtendedReport/>
                </CardWithTitle>

            </div>
        </div>
    );
}


const NoReport = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-2xl font-bold mb-4">No Report Available</h1>
      <p className="text-gray-600">No report data available, please upload files to generate a report.</p>
    </div>
  );
};