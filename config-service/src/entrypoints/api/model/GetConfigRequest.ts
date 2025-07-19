import { OutputFile } from "../../../domain/model/Output";

export interface RechargeConfirmResponse {
  message: string;
  data: Data;
}

export interface Data extends OutputFile { } 
