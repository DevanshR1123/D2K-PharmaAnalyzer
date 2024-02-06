"use client";

import Image from "next/image";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useState } from "react";
import { Image as ImagePlaceholder } from "lucide-react";

// {
//     "incentive": incentive,
//     "image": cropped_img,
//     "visibility_percentage": visibility_percentage,
//     "placement_analysis_percentage": placement_analysis_percentage,
//     "lighting_conditions": lighting_conditions,
//     "insights": response.text,
// }

type ImageData = {
  incentive: number;
  visibility_percentage: number;
  placement_analysis_percentage: number;
  lighting_conditions: string;
  insights: string;
  image: string;
};

export default function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const [data, setData] = useState<ImageData | null>(null);

  return (
    <main className="grid grid-flow-col gap-8 bg-slate-700 p-8">
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          const data = new FormData();
          data.append("image", image! as Blob);
          try {
            setLoading(true);
            const res = await fetch("http://localhost:5000/yolo", {
              method: "POST",
              body: data,
            });
            const json = await res.json();
            setData(json);
          } catch (error) {
            console.error(error);
          } finally {
            setLoading(false);
            setImage(null);
          }
        }}
        className="grid h-min max-w-[400px] gap-4 rounded-xl bg-primary-foreground p-4"
      >
        {image ? (
          <>
            <div className="flex flex-col items-center justify-center border-2 border-dashed border-primary p-4">
              <Image
                src={URL.createObjectURL(image)}
                alt="Uploaded image"
                width={300}
                height={300}
                className="h-[300px] object-contain"
              />
            </div>
            <Button onClick={() => setImage(null)} disabled={loading}>
              Remove image
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Uploading..." : "Upload"}
            </Button>
          </>
        ) : (
          <>
            <div className="flex aspect-square flex-col items-center justify-center border-2 border-dashed border-primary p-4">
              <ImagePlaceholder size={40} />
              <p className="mt-4 text-lg text-muted-foreground">
                No image uploaded
              </p>
            </div>
            <Label className="inline-flex h-10 items-center justify-center whitespace-nowrap rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50">
              Upload an image
              <Input
                type="file"
                name="image"
                onChange={(e) => {
                  console.log(e.target.files?.[0]);
                  setImage(e.target.files?.[0] || null);
                }}
                className="sr-only"
              />
            </Label>
          </>
        )}
      </form>
      <div className="grid max-h-96 grid-cols-2 gap-4 place-self-start overflow-y-auto rounded-xl bg-primary-foreground p-4">
        {data ? (
          <Card className="bg-primary text-secondary">
            <CardHeader>
              <CardTitle>Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                <p>Incentive: {data.incentive}</p>
                <p>Visibility Percentage: {data.visibility_percentage}</p>
                <p>
                  Placement Analysis Percentage:{" "}
                  {data.placement_analysis_percentage}
                </p>
                <p>Lighting Conditions: {data.lighting_conditions}</p>
                <p>Insights: {data.insights}</p>
              </CardDescription>
            </CardContent>
            <CardFooter>
              <Image
                src={data.image}
                alt="Uploaded image"
                width={300}
                height={300}
                className="h-[300px] object-contain"
              />
            </CardFooter>
          </Card>
        ) : (
          <p className="text-lg text-muted-foreground">
            Upload an Image to see the analysis
          </p>
        )}
      </div>
    </main>
  );
}
